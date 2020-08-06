from pprint import pprint as pp
import logging
LOG = logging.getLogger(__name__)
import pytest
from scout.build.genes.transcript import build_transcript

{'chrom': '1', 'transcript_start': 1167629, 'transcript_end': 1170421, 'mrna': {'NM_080605'}, 'mrna_predicted': set(), 'nc_rna': set(), 'ensembl_gene_id': 'ENSG00000176022', 'ensembl_transcript_id': 'ENST00000379198', 'hgnc_id': 17978, 'primary_transcripts': {'NM_080605'}}

def test_build_hgnc_transcripts(parsed_transcripts):
    # GIVEN iterable with parsed transcripts

    # WHEN building transcript objects
    for tx_id in parsed_transcripts:
        tx_info = parsed_transcripts[tx_id]
        LOG.debug("tx_info: {}".format(tx_info))
        tx_obj = build_transcript(tx_info)

        # THEN check that the gene models have a hgnc id
        assert tx_obj["hgnc_id"]





def test_build_hgnc_transcripts_Exceptions(mocker, test_transcript):
    # GIVEN a 
    test_transcript['hgnc_id'] = None
    # THEN calling build_transcript() will raise KeyError
    with pytest.raises(TypeError):
        build_transcript(test_transcript)

    del test_transcript['hgnc_id'] 
    with pytest.raises(KeyError):
        build_transcript(test_transcript)
        

    test_transcript['transcript_end'] = None
    # THEN calling build_transcript() will raise KeyError
    with pytest.raises(TypeError):
        build_transcript(test_transcript)

    del test_transcript['transcript_end'] 
    with pytest.raises(KeyError):
        build_transcript(test_transcript)


    test_transcript['transcript_start'] = None
    # THEN calling build_transcript() will raise KeyError
    with pytest.raises(TypeError):
        build_transcript(test_transcript)

    del test_transcript['transcript_start'] 
    with pytest.raises(KeyError):
        build_transcript(test_transcript)


    del test_transcript['chrom'] 
    with pytest.raises(KeyError):
        build_transcript(test_transcript)


    del test_transcript['ensembl_transcript_id'] 
    with pytest.raises(KeyError):
        build_transcript(test_transcript)


        
