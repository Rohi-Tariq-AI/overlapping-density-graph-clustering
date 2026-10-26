import json
from graph_clustering.overlap_cli import main

def test_overlap_cli_writes_structured_outputs(tmp_path):
    main(['data_gml/karate.gml','--density','0.40','--output',str(tmp_path)])
    assert (tmp_path/'results.json').exists()
    assert (tmp_path/'clusters.csv').exists()
    assert (tmp_path/'summary.txt').exists()
    data=json.loads((tmp_path/'results.json').read_text())
    assert data['clusters'][0]['starting_triangle'] == [1,4,8]
    assert data['clusters'][0]['relative_density'] == 0.42
    assert data['cluster_count'] == 5
