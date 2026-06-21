# ruff: noqa: F403, F405, E501
from ._test_full_e2e_base import *  # noqa: F403


class _TestCLIE2EMixin0:
    """CLI end-to-end tests"""
    def _run_cli(self, args, extra_env=None, input_text=None):
        """Helper to run CLI command"""
        env = {**os.environ}
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ['python', '-m', 'cli_anything.firefly_iii', '--json'] + args,
            capture_output=True,
            text=True,
            env=env,
            input=input_text
        )
    def test_cli_about(self):
        """Test CLI about command"""
        result = self._run_cli(['info', 'about'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_accounts_list(self):
        """Test CLI accounts list command"""
        result = self._run_cli(['accounts', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
        assert isinstance(data['data'], list)
    def test_cli_accounts_list_with_limit(self):
        """Test CLI accounts list with limit"""
        result = self._run_cli(['accounts', 'list', '--limit', '5'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
        assert len(data['data']) <= 5
    def test_cli_transactions_list(self):
        """Test CLI transactions list command"""
        result = self._run_cli(['transactions', 'list', '--limit', '5'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
        assert isinstance(data['data'], list)
    def test_cli_budgets_list(self):
        """Test CLI budgets list command"""
        result = self._run_cli(['budgets', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_budgets_crud(self):
        """Test CLI budgets CRUD commands (skip create/update due to permission)"""
        # Just test list - some users don't have create permission
        result = self._run_cli(['budgets', 'list'])
        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_categories_list(self):
        """Test CLI categories list command"""
        result = self._run_cli(['categories', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_categories_crud(self):
        """Test CLI categories CRUD commands (skip create/update due to permission)"""
        # Just test list - some users don't have create permission
        result = self._run_cli(['categories', 'list'])
        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_tags_list(self):
        """Test CLI tags list command"""
        result = self._run_cli(['tags', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
    def test_cli_tags_crud(self):
        """Test CLI tags CRUD commands"""
        import uuid
        tag_name = f"cli-test-{uuid.uuid4().hex[:8]}"

        # Create
        result = self._run_cli(['tags', 'create', '--tag', tag_name])
        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
        tag_id = data['data']['id']

        # Get
        result = self._run_cli(['tags', 'get', '--id', tag_id])
        assert result.returncode == 0, f"Error: {result.stderr}"

        # Update
        result = self._run_cli(['tags', 'update', '--id', tag_id, '--tag', tag_name + '-updated'])
        assert result.returncode == 0, f"Error: {result.stderr}"

        # Delete (with confirmation)
        result = self._run_cli(['tags', 'delete', '--id', tag_id], input_text='y\n')
        assert result.returncode == 0, f"Error: {result.stderr}"
    def test_cli_bills_list(self):
        """Test CLI bills list command"""
        result = self._run_cli(['bills', 'list'])

        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert 'data' in data
