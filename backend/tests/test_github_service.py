import pytest
from unittest.mock import patch, MagicMock
from services.githubService import get_user_repos

@pytest.mark.asyncio
async def test_get_user_repos():
    # Mock the requests.get call
    with patch('requests.get') as mock_get:
        # Set up mock responses
        mock_user_response = MagicMock()
        mock_user_response.json.return_value = {"login": "testuser"}
        
        mock_repo_response = MagicMock()
        mock_repo_response.json.return_value = [{"name": "repo1"}, {"name": "repo2"}]
        
        # Set up side effect
        def side_effect(url, headers):
            if 'user/repos' in url:
                return mock_repo_response
            return mock_user_response
            
        mock_get.side_effect = side_effect
        
        # Call the function
        result = await get_user_repos("fake_token")
        
        # Check the result
        assert result["username"] == "testuser"
        assert len(result["repos"]) == 2