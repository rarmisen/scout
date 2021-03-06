# -*- coding: utf-8 -*-
import logging

from datetime import datetime as datetime

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


def build_gene(gene_info, adapter):
    """Build a panel_gene object

    Args:
        gene_info(dict)

    Returns:
        gene_obj(dict)

        panel_gene = dict(
            hgnc_id = int, # required
            symbol = str,

            disease_associated_transcripts = list, # list of strings that represent refseq transcripts
            reduced_penetrance = bool,
            mosaicism = bool,
            database_entry_version = str,

            ar = bool,
            ad = bool,
            mt = bool,
            xr = bool,
            xd = bool,
            x = bool,
            y = bool,
        )

    """
    symbol = gene_info.get("hgnc_symbol")
    try:
        # A gene has to have a hgnc id
        hgnc_id = gene_info["hgnc_id"]
        if not hgnc_id:
            raise KeyError()
    except KeyError as err:
        raise KeyError(
            "Gene {0} is missing hgnc id. Panel genes has to have hgnc_id".format(symbol)
        )

    hgnc_gene = adapter.hgnc_gene(hgnc_id)
    if hgnc_gene is None:
        raise IntegrityError("hgnc_id {0} is not in the gene database!".format(hgnc_id))

    gene_obj = dict(hgnc_id=hgnc_id)

    gene_obj["symbol"] = hgnc_gene["hgnc_symbol"]
    if symbol != gene_obj["symbol"]:
        LOG.warning(
            "Symbol in database does not correspond to symbol in panel file for gene %s",
            hgnc_id,
        )
        LOG.warning(
            "Using symbol %s for gene %s, instead of %s"
            % (hgnc_gene["hgnc_symbol"], hgnc_id, symbol)
        )

    if gene_info.get("transcripts"):
        gene_obj["disease_associated_transcripts"] = gene_info["transcripts"]

    if gene_info.get("reduced_penetrance"):
        gene_obj["reduced_penetrance"] = True

    if gene_info.get("mosaicism"):
        gene_obj["mosaicism"] = True

    if gene_info.get("database_entry_version"):
        gene_obj["database_entry_version"] = gene_info["database_entry_version"]

    if gene_info.get("inheritance_models"):
        for model in gene_info["inheritance_models"]:
            if model == "AR":
                gene_obj["ar"] = True
            if model == "AD":
                gene_obj["ad"] = True
            if model == "MT":
                gene_obj["mt"] = True
            if model == "XR":
                gene_obj["xr"] = True
            if model == "XD":
                gene_obj["xd"] = True
            if model == "X":
                gene_obj["x"] = True
            if model == "Y":
                gene_obj["y"] = True

    return gene_obj


def build_panel(panel_info, adapter):
    """Build a gene_panel object

        Args:
            panel_info(dict): A dictionary with panel information
            adapter (scout.adapter.MongoAdapter)

        Returns:
            panel_obj(dict)

    gene_panel = dict(
        panel_id = str, # required
        institute = str, # institute_id, required
        maintainer = list, # list of user._id
        version = float, # required
        date = datetime, # required
        display_name = str, # default is panel_name
        description = str # optional panel description
        genes = list, # list of panel genes, sorted on panel_gene['symbol']
    )

    """

    panel_name = panel_info.get("panel_id", panel_info.get("panel_name"))

    if panel_name:
        panel_name = panel_name.strip()
    else:
        raise KeyError("Panel has to have a id")

    panel_obj = dict(panel_name=panel_name)
    LOG.info("Building panel with name: {0}".format(panel_name))

    try:
        institute_id = panel_info["institute"]
    except KeyError as err:
        raise KeyError("Panel has to have a institute")

    # Check if institute exists in database
    if adapter.institute(institute_id) is None:
        raise IntegrityError("Institute %s could not be found" % institute_id)

    panel_obj["institute"] = panel_info["institute"]

    panel_obj["version"] = float(panel_info["version"])

    try:
        panel_obj["date"] = panel_info["date"]
    except KeyError as err:
        raise KeyError("Panel has to have a date")

    panel_obj["maintainer"] = panel_info.get("maintainer", [])
    panel_obj["display_name"] = panel_info.get("display_name", panel_obj["panel_name"])
    if panel_obj["display_name"]:
        panel_obj["display_name"] = panel_obj["display_name"].strip()
    panel_obj["description"] = panel_info.get("description")

    gene_objs = []
    fail = False
    for gene_info in panel_info.get("genes", []):
        try:
            gene_obj = build_gene(gene_info, adapter)
            gene_objs.append(gene_obj)
        except IntegrityError as err:
            LOG.warning(err)
            fail = True

    if fail:
        raise IntegrityError("Some genes did not exist in database. Please see log messages.")

    panel_obj["genes"] = gene_objs

    return panel_obj
