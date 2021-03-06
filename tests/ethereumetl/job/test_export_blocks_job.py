import pytest

import tests.resources
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_blocks_job_item_exporter import export_blocks_job_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.mock_ipc_wrapper import MockIPCWrapper
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_blocks_job'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group", [
    (0, 0, 1, 'block_without_transactions'),
    (483920, 483920, 1, 'block_with_logs'),
    (47218, 47219, 1, 'blocks_with_transactions'),
    (47218, 47219, 2, 'blocks_with_transactions')
])
def test_export_blocks_job(tmpdir, start_block, end_block, batch_size, resource_group):
    blocks_output_file = tmpdir.join('actual_blocks.csv')
    transactions_output_file = tmpdir.join('actual_transactions.csv')

    job = ExportBlocksJob(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        ipc_wrapper=ThreadLocalProxy(lambda: MockIPCWrapper(lambda file: read_resource(resource_group, file))),
        max_workers=5,
        item_exporter=export_blocks_job_item_exporter(blocks_output_file, transactions_output_file),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.csv'), read_file(blocks_output_file)
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.csv'), read_file(transactions_output_file)
    )
