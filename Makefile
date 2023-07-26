models:
	rloop-grammar-build-model Collection_pFC53_SUPERCOILEDCR_runs_10 -c 10 -p 13 -w 4 --plasmids pFC53_SUPERCOILEDCR -tp 10 -d aggregate_pFC53_SUPERCOILEDCR_p13_w4_runs_10
	rloop-grammar-build-model Collection_pFC8_SUPERCOILEDCR_runs_10 -c 10 -p 13 -w 4 --plasmids pFC8_SUPERCOILEDCR -tp 10 -d aggregate_pFC8_SUPERCOILEDCR_p13_w4_runs_10
	rloop-grammar-build-model Collection_pFC53_GYRASECR_runs_10 -c 10 -p 13 -w 4 --plasmids pFC53_GYRASECR -tp 10 -d aggregate_pFC53_GYRASECR_p13_w4_runs_10
	rloop-grammar-build-model Collection_pFC8_GYRASECR_runs_10 -c 10 -p 13 -w 4 --plasmids pFC8_GYRASECR -tp 10 -d aggregate_pFC8_GYRASECR_p13_w4_runs_10
	rloop-grammar-build-model Collection_pFC53_LINEARIZED_runs_10 -c 10 -p 13 -w 4 --plasmids pFC53_LINEARIZED -tp 10 -d aggregate_pFC53_LINEARIZED_p13_w4_runs_10
	rloop-grammar-build-model Collection_pFC8_LINEARIZED_runs_10 -c 10 -p 13 -w 4 --plasmids pFC8_LINEARIZED -tp 10 -d aggregate_pFC8_LINEARIZED_p13_w4_runs_10

union:
	rloop-grammar-union-models UnionCollection_SUPERCOILEDCR_runs_10 -i Collection_pFC53_SUPERCOILEDCR_runs_10 Collection_pFC8_SUPERCOILEDCR_runs_10
	rloop-grammar-union-models UnionCollection_GYRASECR_runs_10 -i Collection_pFC53_GYRASECR_runs_10 Collection_pFC8_GYRASECR_runs_10
	rloop-grammar-union-models UnionCollection_LINEARIZED_runs_10 -i Collection_pFC53_LINEARIZED_runs_10 Collection_pFC8_LINEARIZED_runs_10


predict:
	rloop-grammar-predict UnionCollection_SUPERCOILEDCR_predict_on_pFC53 -i UnionCollection_SUPERCOILEDCR_runs_10 --plasmids pFC53_SUPERCOILEDCR
	rloop-grammar-predict UnionCollection_SUPERCOILEDCR_predict_on_pFC8 -i UnionCollection_SUPERCOILEDCR_runs_10 --plasmids pFC8_SUPERCOILEDCR
	rloop-grammar-predict UnionCollection_GYRASECR_predict_on_pFC53 -i UnionCollection_GYRASECR_runs_10 --plasmids pFC53_GYRASECR
	rloop-grammar-predict UnionCollection_GYRASECR_predict_on_pFC8 -i UnionCollection_GYRASECR_runs_10 --plasmids pFC8_GYRASECR
	rloop-grammar-predict UnionCollection_LINEARIZED_predict_on_pFC53 -i UnionCollection_LINEARIZED_runs_10 --plasmids pFC53_LINEARIZED
	rloop-grammar-predict UnionCollection_LINEARIZED_predict_on_pFC8 -i UnionCollection_LINEARIZED_runs_10 --plasmids pFC8_LINEARIZED

.PHONY: models union predict
