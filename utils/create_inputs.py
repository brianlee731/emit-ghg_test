import json
import subprocess
import pdb

# NOTE: I had to "pip install unity-sds-client==0.5.0a6" in my local isofit env and then update the ipykernel accordingly, it wouldn't work with the default PyPI version of unity-sds-client
from unity_sds_client.unity import Unity
from unity_sds_client.unity_services import UnityServices
from unity_sds_client.resources.job_status import JobStatus
from unity_sds_client.unity import UnityEnvironments

def create_inputs(process, fid):
    
    execute_cmd_json_filename = '/home/jovyan/execute_cmd.json'
    workflow_params_json_filename = '/home/jovyan//workflow_params.json'

    cwl_workflow_path = r'http://awslbdockstorestack-lb-1429770210.us-west-2.elb.amazonaws.com:9998/api/ga4gh/trs/v2/tools/%23workflow%2Fdockstore.org%2Fedwinsarkissian%2Femit-ghg_test/versions/23/PLAIN-CWL/descriptor/%2Fworkflow.cwl'

    execute_cmd_json = json.load(open(execute_cmd_json_filename, 'r'))
    workflow_params_json = json.load(open(workflow_params_json_filename, 'r'))

    l1b_tmp_stac_filename = 'l1b_tmp_stac.json'
    l2a_tmp_stac_filename = 'l2a_tmp_stac.json'
    l1b_curl_cmd = f'curl -X GET "https://cmr.earthdata.nasa.gov/search/granules.stac?collection_concept_id=C2408009906-LPCLOUD&options%5Breadable_granule_name%5D%5Bpattern%5D=true&readable_granule_name%5B%5D=*{fid}*" > {l1b_tmp_stac_filename}'
    l2a_curl_cmd = f'curl -X GET "https://cmr.earthdata.nasa.gov/search/granules.stac?collection_concept_id=C2408750690-LPCLOUD&options%5Breadable_granule_name%5D%5Bpattern%5D=true&readable_granule_name%5B%5D=*{fid}*" > {l2a_tmp_stac_filename}'

    subprocess.call(l1b_curl_cmd, shell = True)
    subprocess.call(l2a_curl_cmd, shell = True)

    stac_merge_cmd = f'python stac_merge.py ./ {l1b_tmp_stac_filename} {l2a_tmp_stac_filename}'
    subprocess.call(stac_merge_cmd, shell = True)
    catalog_json = json.load(open('./catalog.json', 'r'))

    workflow_params_json['stage_in']['stac_json'] = json.dumps(catalog_json)

    execute_cmd_json['inputs']['cwl_args'] = json.dumps(workflow_params_json)
    execute_cmd_json['inputs']['cwl_workflow'] = cwl_workflow_path

    return execute_cmd_json

def setup():
    unity = Unity(UnityEnvironments.PROD)
    unity.set_venue_id("")
    process_service = unity.client(UnityServices.PROCESS_SERVICE)
    process_service.endpoint = "http://k8s-sps-ogcproce-5ff49ba35c-1884290802.us-west-2.elb.amazonaws.com:5001"
    process = process_service.get_process("cwl_dag")

    fids = ['20230809t090523', '20230809t090658', '20230809t091129', '20230809t091129', '20230809t105356']
    submitted_jobs = []
    
    for fid in fids:
        execute_cmd_json = create_inputs(process, fid)

        execute_cmd_filename = f'execute_cmd_{fid}.json'
        json.dump(execute_cmd_json, open(execute_cmd_filename, 'w'))

        submitted_job = process.execute(execute_cmd_json)
        submitted_jobs.append(submitted_job)

    return submitted_jobs