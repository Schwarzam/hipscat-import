"""Test full exection of the dask-parallelized runner"""

import os
import shutil

import pandas as pd
import pytest

import hipscat_import.catalog.resume_files as rf
import hipscat_import.catalog.run_import as runner
from hipscat_import.catalog.arguments import ImportArguments
from hipscat_import.catalog.file_readers import get_file_reader


def test_empty_args():
    """Runner should fail with empty arguments"""
    with pytest.raises(ValueError):
        runner.run(None)


def test_bad_args():
    """Runner should fail with mis-typed arguments"""
    args = {"catalog_name": "bad_arg_type"}
    with pytest.raises(ValueError):
        runner.run(args)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.timeout(5)
def test_resume_dask_runner(
    dask_client,
    small_sky_parts_dir,
    resume_dir,
    tmp_path,
    assert_text_file_matches,
    assert_parquet_file_ids,
):
    """Test execution in the presence of some resume files."""
    ## First, copy over our intermediate files.
    ## This prevents overwriting source-controlled resume files.
    temp_path = os.path.join(tmp_path, "resume", "intermediate")
    shutil.copytree(
        os.path.join(resume_dir, "intermediate"),
        temp_path,
    )
    for file_index in range(0, 5):
        rf.write_mapping_start_key(
            temp_path,
            os.path.join(small_sky_parts_dir, f"catalog_0{file_index}_of_05.csv"),
        )
        rf.write_mapping_done_key(
            temp_path,
            os.path.join(small_sky_parts_dir, f"catalog_0{file_index}_of_05.csv"),
        )

    shutil.copytree(
        os.path.join(resume_dir, "Norder=0"),
        os.path.join(tmp_path, "resume", "Norder=0"),
    )

    with pytest.raises(ValueError):
        ## Check that we fail if there are some existing intermediate files
        ImportArguments(
            catalog_name="resume",
            input_path=small_sky_parts_dir,
            input_format="csv",
            output_path=tmp_path,
            dask_tmp=tmp_path,
            tmp_dir=tmp_path,
            overwrite=True,
            highest_healpix_order=0,
            pixel_threshold=1000,
            progress_bar=False,
        )

    args = ImportArguments(
        catalog_name="resume",
        input_path=small_sky_parts_dir,
        input_format="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        tmp_dir=tmp_path,
        overwrite=True,
        resume=True,
        highest_healpix_order=0,
        pixel_threshold=1000,
        progress_bar=False,
    )

    runner.run_with_client(args, dask_client)

    # Check that the catalog metadata file exists
    expected_metadata_lines = [
        "{",
        '    "catalog_name": "resume",',
        '    "catalog_type": "object",',
        '    "epoch": "J2000",',
        '    "ra_kw": "ra",',
        '    "dec_kw": "dec",',
        '    "total_rows": 131',
        "}",
    ]
    metadata_filename = os.path.join(args.catalog_path, "catalog_info.json")
    assert_text_file_matches(expected_metadata_lines, metadata_filename)

    # Check that the partition info file exists
    expected_partition_lines = [
        "Norder,Dir,Npix,num_objects",
        "0,0,11,131",
    ]
    partition_filename = os.path.join(args.catalog_path, "partition_info.csv")
    assert_text_file_matches(expected_partition_lines, partition_filename)

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = os.path.join(
        args.catalog_path, "Norder=0", "Dir=0", "Npix=11.parquet"
    )

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)

    ## Re-running the pipeline with fully done intermediate files
    ## should result in no changes to output files.
    shutil.copytree(
        os.path.join(resume_dir, "intermediate"),
        temp_path,
    )
    rf.set_mapping_done(temp_path)
    rf.set_reducing_done(temp_path)

    args = ImportArguments(
        catalog_name="resume",
        input_path=small_sky_parts_dir,
        input_format="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        tmp_dir=tmp_path,
        overwrite=True,
        resume=True,
        highest_healpix_order=0,
        pixel_threshold=1000,
        progress_bar=False,
    )

    runner.run_with_client(args, dask_client)

    assert_text_file_matches(expected_metadata_lines, metadata_filename)
    assert_text_file_matches(expected_partition_lines, partition_filename)
    assert_parquet_file_ids(output_file, "id", expected_ids)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.timeout(5)
def test_dask_runner(
    dask_client,
    small_sky_parts_dir,
    assert_parquet_file_ids,
    assert_text_file_matches,
    tmp_path,
):
    """Test basic execution."""
    args = ImportArguments(
        catalog_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir,
        input_format="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
    )

    runner.run_with_client(args, dask_client)

    # Check that the catalog metadata file exists
    expected_lines = [
        "{",
        '    "catalog_name": "small_sky_object_catalog",',
        '    "catalog_type": "object",',
        '    "epoch": "J2000",',
        '    "ra_kw": "ra",',
        '    "dec_kw": "dec",',
        '    "total_rows": 131',
        "}",
    ]
    metadata_filename = os.path.join(args.catalog_path, "catalog_info.json")
    assert_text_file_matches(expected_lines, metadata_filename)

    # Check that the partition info file exists
    expected_lines = [
        "Norder,Dir,Npix,num_objects",
        "0,0,11,131",
    ]
    metadata_filename = os.path.join(args.catalog_path, "partition_info.csv")
    assert_text_file_matches(expected_lines, metadata_filename)

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = os.path.join(
        args.catalog_path, "Norder=0", "Dir=0", "Npix=11.parquet"
    )

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", expected_ids)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.timeout(5)
def test_dask_runner_source_table(
    dask_client,
    small_sky_source_dir,
    assert_text_file_matches,
    tmp_path,
):
    """Test basic execution."""
    args = ImportArguments(
        catalog_name="small_sky_source_catalog",
        input_path=small_sky_source_dir,
        input_format="csv",
        catalog_type="source",
        ra_column="source_ra",
        dec_column="source_dec",
        id_column="source_id",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=2,
        pixel_threshold=3_000,
        overwrite=True,
        progress_bar=False,
    )

    runner.run_with_client(args, dask_client)

    # Check that the catalog metadata file exists
    expected_lines = [
        "{",
        '    "catalog_name": "small_sky_source_catalog",',
        '    "catalog_type": "source",',
        '    "epoch": "J2000",',
        '    "ra_kw": "source_ra",',
        '    "dec_kw": "source_dec",',
        '    "total_rows": 17161',
        "}",
    ]
    metadata_filename = os.path.join(args.catalog_path, "catalog_info.json")
    assert_text_file_matches(expected_lines, metadata_filename)

    # Check that the partition info file exists
    expected_lines = [
        "Norder,Dir,Npix,num_objects",
        "0,0,4,50",
        "1,0,47,2395",
        "2,0,176,385",
        "2,0,177,1510",
        "2,0,178,1634",
        "2,0,179,1773",
        "2,0,180,655",
        "2,0,181,903",
        "2,0,182,1246",
        "2,0,183,1143",
        "2,0,184,1390",
        "2,0,185,2942",
        "2,0,186,452",
        "2,0,187,683",
    ]
    metadata_filename = os.path.join(args.catalog_path, "partition_info.csv")
    assert_text_file_matches(expected_lines, metadata_filename)


@pytest.mark.timeout(5)
def test_dask_runner_stats_only(dask_client, small_sky_parts_dir, tmp_path):
    """Test basic execution, without generating catalog parquet outputs."""
    args = ImportArguments(
        catalog_name="small_sky",
        input_path=small_sky_parts_dir,
        input_format="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
        debug_stats_only=True,
    )

    runner.run_with_client(args, dask_client)

    metadata_filename = os.path.join(args.catalog_path, "catalog_info.json")
    assert os.path.exists(metadata_filename)

    # Check that the catalog parquet file DOES NOT exist
    output_file = os.path.join(
        args.catalog_path, "Norder=0", "Dir=0", "Npix=11.parquet"
    )

    assert not os.path.exists(output_file)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.timeout(5)
def test_dask_runner_mixed_schema_csv(
    dask_client,
    mixed_schema_csv_dir,
    mixed_schema_csv_parquet,
    assert_parquet_file_ids,
    tmp_path,
):
    """Test basic execution, with a mixed schema"""

    schema_parquet = pd.read_parquet(mixed_schema_csv_parquet)
    args = ImportArguments(
        catalog_name="mixed_csv",
        input_path=mixed_schema_csv_dir,
        input_format="csv",
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        file_reader=get_file_reader(
            "csv", chunksize=1, type_map=schema_parquet.dtypes.to_dict()
        ),
        progress_bar=False,
        use_schema_file=mixed_schema_csv_parquet,
    )

    runner.run_with_client(args, dask_client)

    # Check that the catalog parquet file exists
    output_file = os.path.join(
        args.catalog_path, "Norder=0", "Dir=0", "Npix=11.parquet"
    )

    assert_parquet_file_ids(output_file, "id", [*range(700, 708)])
