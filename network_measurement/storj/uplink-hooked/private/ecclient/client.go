// Copyright (C) 2019 Storj Labs, Inc.
// See LICENSE for copying information.

package ecclient

import (
	"context"
	"errors"
	"fmt"
	"io"
	//"log"
	"sort"
	"strconv"
	"sync"
	"time"

	"github.com/spacemonkeygo/monkit/v3"
	"github.com/zeebo/errs"
	"storj.io/common/encryption"
	"storj.io/common/errs2"
	"storj.io/common/pb"
	"storj.io/common/ranger"
	"storj.io/common/rpc"
	"storj.io/common/storj"
	"storj.io/eventkit"
	"storj.io/uplink/private/eestream"
	"storj.io/uplink/private/piecestore"

	AmwsomeHook "storj.io/uplink/hook"
)

var mon = monkit.Package()
var evs = eventkit.Package()

// GetOptions is a struct of options for GetWithOptions.
type GetOptions struct {
	ErrorDetection bool
}

// Client defines an interface for storing erasure coded data to piece store nodes.
type Client interface {
	PutSingleResultFake(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, rs eestream.RedundancyStrategy, buketName string) (results []*pb.SegmentPieceUploadResult, err error)
	PutSingleResult(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, rs eestream.RedundancyStrategy, data io.Reader) (results []*pb.SegmentPieceUploadResult, err error)
	Get(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, es eestream.ErasureScheme, size int64) (ranger.Ranger, error)
	GetWithOptions(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, es eestream.ErasureScheme, size int64, opts GetOptions) (ranger.Ranger, error)
	WithForceErrorDetection(force bool) Client
	// PutPiece is not intended to be used by normal uplinks directly, but is exported to support storagenode graceful exit transfers.
	PutPiece(ctx, parent context.Context, limit *pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, data io.ReadCloser) (hash *pb.PieceHash, id *struct{}, err error)
}

type dialPiecestoreFunc func(context.Context, storj.NodeURL) (*piecestore.Client, error)

type ecClient struct {
	dialer              rpc.Dialer
	memoryLimit         int
	forceErrorDetection bool
}

// New creates a client from the given dialer and max buffer memory.
func New(dialer rpc.Dialer, memoryLimit int) Client {
	return &ecClient{
		dialer:      dialer,
		memoryLimit: memoryLimit,
	}
}

func (ec *ecClient) WithForceErrorDetection(force bool) Client {
	ec.forceErrorDetection = force
	return ec
}

func (ec *ecClient) dialPiecestore(ctx context.Context, n storj.NodeURL) (*piecestore.Client, error) {
	hashAlgo := piecestore.GetPieceHashAlgo(ctx)
	client, err := piecestore.DialReplaySafe(ctx, ec.dialer, n, piecestore.DefaultConfig)
	if err != nil {
		return client, err
	}
	client.UploadHashAlgo = hashAlgo
	return client, nil
}

func (ec *ecClient) PutSingleResult(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, rs eestream.RedundancyStrategy, data io.Reader) (results []*pb.SegmentPieceUploadResult, err error) {
	fmt.Println("client.go PutSingleResult")
	successfulNodes, successfulHashes, err := ec.put(ctx, limits, privateKey, rs, data, time.Time{})
	if err != nil {
		return nil, err
	}

	uploadResults := make([]*pb.SegmentPieceUploadResult, 0, len(successfulNodes))
	for i := range successfulNodes {
		if successfulNodes[i] == nil {
			continue
		}

		uploadResults = append(uploadResults, &pb.SegmentPieceUploadResult{
			PieceNum: int32(i),
			NodeId:   successfulNodes[i].Id,
			Hash:     successfulHashes[i],
		})
	}

	if l := len(uploadResults); l < rs.OptimalThreshold() {
		return nil, Error.New("uploaded results (%d) are below the optimal threshold (%d)", l, rs.OptimalThreshold())
	}

	return uploadResults, nil
}

func (ec *ecClient) PutSingleResultFake(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, rs eestream.RedundancyStrategy, buketName string) (results []*pb.SegmentPieceUploadResult, err error) {
	//fmt.Println("client.go PutSingleResultFake")
	successfulNodes, successfulHashes, err := ec.FakePut(ctx, limits, rs, buketName)
	if err != nil {
		return nil, err
	}

	uploadResults := make([]*pb.SegmentPieceUploadResult, 0, len(successfulNodes))
	for i := range successfulNodes {
		if successfulNodes[i] == nil {
			continue
		}

		uploadResults = append(uploadResults, &pb.SegmentPieceUploadResult{
			PieceNum: int32(i),
			NodeId:   successfulNodes[i].Id,
			Hash:     successfulHashes[i],
		})
	}

	if l := len(uploadResults); l < rs.OptimalThreshold() {
		return nil, Error.New("uploaded results (%d) are below the optimal threshold (%d)", l, rs.OptimalThreshold())
	}

	return uploadResults, nil
}

func (ec *ecClient) FakePut(ctx context.Context, limits []*pb.AddressedOrderLimit, rs eestream.RedundancyStrategy, bucketName string) (successfulNodes []*pb.Node, successfulHashes []*pb.PieceHash, err error) {
	defer mon.Task()(&ctx,
		"erasure:"+strconv.Itoa(rs.ErasureShareSize()),
		"stripe:"+strconv.Itoa(rs.StripeSize()),
		"repair:"+strconv.Itoa(rs.RepairThreshold()),
		"optimal:"+strconv.Itoa(rs.OptimalThreshold()),
	)(&err)

	pieceCount := len(limits)
	if pieceCount != rs.TotalCount() {
		return nil, nil, Error.New("size of limits slice (%d) does not match total count (%d) of erasure scheme", pieceCount, rs.TotalCount())
	}

	nonNilLimits := nonNilCount(limits)
	if nonNilLimits <= rs.RepairThreshold() && nonNilLimits < rs.OptimalThreshold() {
		return nil, nil, Error.New("number of non-nil limits (%d) is less than or equal to the repair threshold (%d) of erasure scheme", nonNilLimits, rs.RepairThreshold())
	}

	if !unique(limits) {
		return nil, nil, Error.New("duplicated nodes are not allowed")
	}

	//padded := encryption.PadReader(io.NopCloser(data), rs.StripeSize())
	//readers, err := eestream.EncodeReader2(ctx, padded, rs)
	//if err != nil {
	//	return nil, nil, err
	//}
	//
	//type info struct {
	//	i    int
	//	err  error
	//	hash *pb.PieceHash
	//}
	//infos := make(chan info, pieceCount)
	//
	//piecesCtx, piecesCancel := context.WithCancel(ctx)
	//defer piecesCancel()
	var foundDup = true
	for _, addressedLimit := range limits {
		//AmwsomeHook.Hook(fmt.Sprintf("Node ID: %s, Addr: %s\n", addressedLimit.GetLimit().StorageNodeId,
		//	addressedLimit.GetStorageNodeAddress().Address))
		if !AmwsomeHook.Hook(addressedLimit.GetLimit().StorageNodeId.String(), addressedLimit.GetStorageNodeAddress().Address) {
			foundDup = false
			// reset if we found a new node
			if AmwsomeHook.DupRoundCountDict[bucketName] > 0 {
				AmwsomeHook.DupRoundCountDict[bucketName] -= 1
			} else {
				AmwsomeHook.DupRoundCountDict[bucketName] = 0
			}

		}
	}
	// print
	fmt.Printf("Bucket: %s, Current Unique Node = %d\n", bucketName, len(AmwsomeHook.Dict))
	// if after 10 round of no discovery any new node, we should stop
	if foundDup {
		AmwsomeHook.DupRoundCountDict[bucketName]++
		fmt.Printf("Bukect: %s DupRoundCount: %d\n", bucketName, AmwsomeHook.DupRoundCountDict[bucketName])
		if AmwsomeHook.DupRoundCountDict[bucketName] >= 5 {
			AmwsomeHook.ShouldStopDict[bucketName] = true
		}
	}
	return nil, nil, nil
}
func (ec *ecClient) put(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, rs eestream.RedundancyStrategy, data io.Reader, expiration time.Time) (successfulNodes []*pb.Node, successfulHashes []*pb.PieceHash, err error) {
	// MODIFICATION
	// hook the function such that it will go through fake put but print addrs?
	//fmt.Println("Client.go put")
	//fakePut := true
	//if fakePut {
	//	return ec.FakePut(ctx, limits, rs, bucketName)
	//}
	//defer mon.Task()(&ctx,
	//	"erasure:"+strconv.Itoa(rs.ErasureShareSize()),
	//	"stripe:"+strconv.Itoa(rs.StripeSize()),
	//	"repair:"+strconv.Itoa(rs.RepairThreshold()),
	//	"optimal:"+strconv.Itoa(rs.OptimalThreshold()),
	//)(&err)

	pieceCount := len(limits)
	if pieceCount != rs.TotalCount() {
		return nil, nil, Error.New("size of limits slice (%d) does not match total count (%d) of erasure scheme", pieceCount, rs.TotalCount())
	}

	nonNilLimits := nonNilCount(limits)
	if nonNilLimits <= rs.RepairThreshold() && nonNilLimits < rs.OptimalThreshold() {
		return nil, nil, Error.New("number of non-nil limits (%d) is less than or equal to the repair threshold (%d) of erasure scheme", nonNilLimits, rs.RepairThreshold())
	}

	if !unique(limits) {
		return nil, nil, Error.New("duplicated nodes are not allowed")
	}

	padded := encryption.PadReader(io.NopCloser(data), rs.StripeSize())
	readers, err := eestream.EncodeReader2(ctx, padded, rs)
	if err != nil {
		return nil, nil, err
	}

	type info struct {
		i    int
		err  error
		hash *pb.PieceHash
	}
	infos := make(chan info, pieceCount)

	piecesCtx, piecesCancel := context.WithCancel(ctx)
	defer piecesCancel()

	for i, addressedLimit := range limits {
		go func(i int, addressedLimit *pb.AddressedOrderLimit) {
			hash, _, err := ec.PutPiece(piecesCtx, ctx, addressedLimit, privateKey, readers[i])
			infos <- info{i: i, err: err, hash: hash}
		}(i, addressedLimit)
	}

	successfulNodes = make([]*pb.Node, pieceCount)
	successfulHashes = make([]*pb.PieceHash, pieceCount)
	var successfulCount, failureCount, cancellationCount int32

	// all the piece upload errors, combined
	var pieceErrors errs.Group
	for range limits {
		info := <-infos

		if limits[info.i] == nil {
			continue
		}

		if info.err != nil {
			pieceErrors.Add(info.err)
			if !errs2.IsCanceled(info.err) {
				failureCount++
			} else {
				cancellationCount++
			}
			continue
		}

		successfulNodes[info.i] = &pb.Node{
			Id:      limits[info.i].GetLimit().StorageNodeId,
			Address: limits[info.i].GetStorageNodeAddress(),
		}
		successfulHashes[info.i] = info.hash

		successfulCount++
		if int(successfulCount) >= rs.OptimalThreshold() {
			// cancelling remaining uploads
			piecesCancel()
		}
	}

	defer func() {
		select {
		case <-ctx.Done():
			// make sure context.Canceled is the primary error in the error chain
			// for later errors.Is/errs2.IsCanceled checking
			err = errs.Combine(context.Canceled, Error.New("upload cancelled by user"))
		default:
		}
	}()

	mon.IntVal("put_segment_pieces_total").Observe(int64(pieceCount))
	mon.IntVal("put_segment_pieces_optimal").Observe(int64(rs.OptimalThreshold()))
	mon.IntVal("put_segment_pieces_successful").Observe(int64(successfulCount))
	mon.IntVal("put_segment_pieces_failed").Observe(int64(failureCount))
	mon.IntVal("put_segment_pieces_canceled").Observe(int64(cancellationCount))

	if int(successfulCount) <= rs.RepairThreshold() && int(successfulCount) < rs.OptimalThreshold() {
		return nil, nil, Error.New("successful puts (%d) less than or equal to repair threshold (%d), %w", successfulCount, rs.RepairThreshold(), pieceErrors.Err())
	}

	if int(successfulCount) < rs.OptimalThreshold() {
		return nil, nil, Error.New("successful puts (%d) less than success threshold (%d), %w", successfulCount, rs.OptimalThreshold(), pieceErrors.Err())
	}

	return successfulNodes, successfulHashes, nil
}

func (ec *ecClient) PutPiece(ctx, parent context.Context, limit *pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, data io.ReadCloser) (hash *pb.PieceHash, deprecated *struct{}, err error) {
	if limit == nil {
		defer mon.Task()(&ctx, "node: nil")(&err)
		defer func() { err = errs.Combine(err, data.Close()) }()
		_, _ = io.Copy(io.Discard, data)
		return nil, nil, nil
	}

	storageNodeID := limit.GetLimit().StorageNodeId
	defer mon.Task()(&ctx, "node: "+storageNodeID.String()[0:8])(&err)
	start := time.Now()
	measuredReader := countingReader{R: data}
	defer func() {
		var errstr string
		if err != nil {
			errstr = err.Error()
		}
		var pieceSize int64
		var pieceTimestamp time.Time
		var hashAlgo int64
		if hash != nil {
			pieceSize = hash.PieceSize
			pieceTimestamp = hash.Timestamp
			hashAlgo = int64(hash.HashAlgorithm)
		}
		evs.Event("piece-upload",
			eventkit.Bytes("node_id", storageNodeID.Bytes()),
			eventkit.Bytes("piece_id", limit.GetLimit().PieceId.Bytes()),
			eventkit.Duration("upload_time", time.Since(start)),
			eventkit.Bool("success", err == nil),
			eventkit.String("error", errstr),
			eventkit.Int64("bytes", measuredReader.N),
			eventkit.Int64("piece_size", pieceSize),
			eventkit.Timestamp("piece_timestamp", pieceTimestamp),
			eventkit.Int64("hash_algo", hashAlgo),
		)
	}()
	defer func() { err = errs.Combine(err, data.Close()) }()

	ps, err := ec.dialPiecestore(ctx, limitToNodeURL(limit))
	if err != nil {
		return nil, nil, Error.New("failed to dial (node:%v): %w", storageNodeID, err)
	}
	defer func() { err = errs.Combine(err, ps.Close()) }()

	hash, err = ps.UploadReader(ctx, limit.GetLimit(), privateKey, &measuredReader)
	if err != nil {
		if errors.Is(ctx.Err(), context.Canceled) {
			// Canceled context means the piece upload was interrupted by user or due
			// to slow connection. No error logging for this case.
			if errors.Is(parent.Err(), context.Canceled) {
				err = Error.New("upload canceled by user: %w", err)
			} else {
				err = Error.New("upload cut due to slow connection (node:%v): %w", storageNodeID, err)
			}

			// make sure context.Canceled is the primary error in the error chain
			// for later errors.Is/errs2.IsCanceled checking
			err = errs.Combine(context.Canceled, err)
		} else {
			nodeAddress := ""
			if limit.GetStorageNodeAddress() != nil {
				nodeAddress = limit.GetStorageNodeAddress().GetAddress()
			}
			err = Error.New("upload failed (node:%v, address:%v): %w", storageNodeID, nodeAddress, err)
		}

		return nil, nil, err
	}

	return hash, nil, nil
}

type countingReader struct {
	N int64
	R io.Reader
}

func (c *countingReader) Read(p []byte) (n int, err error) {
	n, err = c.R.Read(p)
	c.N += int64(n)
	return n, err
}

func (ec *ecClient) Get(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, es eestream.ErasureScheme, size int64) (rr ranger.Ranger, err error) {
	return ec.GetWithOptions(ctx, limits, privateKey, es, size, GetOptions{})
}

func (ec *ecClient) GetWithOptions(ctx context.Context, limits []*pb.AddressedOrderLimit, privateKey storj.PiecePrivateKey, es eestream.ErasureScheme, size int64, opts GetOptions) (rr ranger.Ranger, err error) {
	defer mon.Task()(&ctx)(&err)

	if len(limits) != es.TotalCount() {
		return nil, Error.New("size of limits slice (%d) does not match total count (%d) of erasure scheme", len(limits), es.TotalCount())
	}

	if nonNilCount(limits) < es.RequiredCount() {
		return nil, Error.New("number of non-nil limits (%d) is less than required count (%d) of erasure scheme", nonNilCount(limits), es.RequiredCount())
	}

	paddedSize := calcPadded(size, es.StripeSize())
	pieceSize := paddedSize / int64(es.RequiredCount())

	rrs := map[int]ranger.Ranger{}
	for i, addressedLimit := range limits {
		if addressedLimit == nil {
			continue
		}

		rrs[i] = &lazyPieceRanger{
			dialPiecestore: ec.dialPiecestore,
			limit:          addressedLimit,
			privateKey:     privateKey,
			size:           pieceSize,
		}
	}

	rr, err = eestream.Decode(rrs, es, ec.memoryLimit, opts.ErrorDetection || ec.forceErrorDetection)
	if err != nil {
		return nil, Error.Wrap(err)
	}

	ranger, err := encryption.Unpad(rr, int(paddedSize-size))
	return ranger, Error.Wrap(err)
}

func unique(limits []*pb.AddressedOrderLimit) bool {
	if len(limits) < 2 {
		return true
	}
	ids := make(storj.NodeIDList, len(limits))
	for i, addressedLimit := range limits {
		if addressedLimit != nil {
			ids[i] = addressedLimit.GetLimit().StorageNodeId
		}
	}

	// sort the ids and check for identical neighbors
	sort.Sort(ids)
	// sort.Slice(ids, func(i, k int) bool { return ids[i].Less(ids[k]) })
	for i := 1; i < len(ids); i++ {
		if ids[i] != (storj.NodeID{}) && ids[i] == ids[i-1] {
			return false
		}
	}

	return true
}

func calcPadded(size int64, blockSize int) int64 {
	mod := size % int64(blockSize)
	if mod == 0 {
		return size
	}
	return size + int64(blockSize) - mod
}

type lazyPieceRanger struct {
	dialPiecestore dialPiecestoreFunc
	limit          *pb.AddressedOrderLimit
	privateKey     storj.PiecePrivateKey
	size           int64
}

// Size implements Ranger.Size.
func (lr *lazyPieceRanger) Size() int64 {
	return lr.size
}

// Range implements Ranger.Range to be lazily connected.
func (lr *lazyPieceRanger) Range(ctx context.Context, offset, length int64) (_ io.ReadCloser, err error) {
	defer mon.Task()(&ctx)(&err)

	ctx, cancel := context.WithCancel(ctx)

	return &lazyPieceReader{
		ranger: lr,
		ctx:    ctx,
		cancel: cancel,
		offset: offset,
		length: length,
	}, nil
}

type lazyPieceReader struct {
	ranger *lazyPieceRanger
	ctx    context.Context
	cancel func()
	offset int64
	length int64

	mu       sync.Mutex
	isClosed bool
	download *piecestore.Download
	client   *piecestore.Client
}

func (lr *lazyPieceReader) Read(data []byte) (_ int, err error) {
	if err := lr.dial(); err != nil {
		return 0, err
	}
	return lr.download.Read(data)
}

func (lr *lazyPieceReader) dial() error {
	lr.mu.Lock()
	if lr.isClosed {
		lr.mu.Unlock()
		return io.EOF
	}
	if lr.download != nil {
		lr.mu.Unlock()
		return nil
	}
	lr.mu.Unlock()

	client, downloader, err := lr.ranger.dial(lr.ctx, lr.offset, lr.length)
	if err != nil {
		return Error.Wrap(err)
	}

	lr.mu.Lock()
	defer lr.mu.Unlock()

	if lr.isClosed {
		// Close tried to cancel the dialing, however failed to do so.
		lr.cancel()
		_ = downloader.Close()
		_ = client.Close()
		return io.ErrClosedPipe
	}

	lr.download = downloader
	lr.client = client

	return nil
}

func limitToNodeURL(limit *pb.AddressedOrderLimit) storj.NodeURL {
	return (&pb.Node{
		Id:      limit.GetLimit().StorageNodeId,
		Address: limit.GetStorageNodeAddress(),
	}).NodeURL()
}

var monLazyPieceRangerDialTask = mon.Task()

func (lr *lazyPieceRanger) dial(ctx context.Context, offset, length int64) (_ *piecestore.Client, _ *piecestore.Download, err error) {
	defer monLazyPieceRangerDialTask(&ctx)(&err)

	ps, err := lr.dialPiecestore(ctx, limitToNodeURL(lr.limit))
	if err != nil {
		return nil, nil, err
	}

	download, err := ps.Download(ctx, lr.limit.GetLimit(), lr.privateKey, offset, length)
	if err != nil {
		return nil, nil, errs.Combine(err, ps.Close())
	}
	return ps, download, nil
}

// GetHashAndLimit gets the download's hash and original order limit.
func (lr *lazyPieceReader) GetHashAndLimit() (*pb.PieceHash, *pb.OrderLimit) {
	if lr.download == nil {
		return nil, nil
	}
	return lr.download.GetHashAndLimit()
}

func (lr *lazyPieceReader) Close() (err error) {
	lr.mu.Lock()
	defer lr.mu.Unlock()
	if lr.isClosed {
		return nil
	}
	lr.isClosed = true

	if lr.download != nil {
		err = errs.Combine(err, lr.download.Close())
	}
	if lr.client != nil {
		err = errs.Combine(err, lr.client.Close())
	}

	lr.cancel()
	return err
}

func nonNilCount(limits []*pb.AddressedOrderLimit) int {
	total := 0
	for _, limit := range limits {
		if limit != nil {
			total++
		}
	}
	return total
}
