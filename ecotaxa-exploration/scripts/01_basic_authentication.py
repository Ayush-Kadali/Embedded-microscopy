#!/usr/bin/env python3
"""
EcoTaxa Basic Authentication Test
Tests connection to EcoTaxa API and verifies credentials
"""

import sys
import os

# Check if ecotaxa_py_client is installed
try:
    import ecotaxa_py_client
    from ecotaxa_py_client.api import authentification_api
    from ecotaxa_py_client.model.login_req import LoginReq
except ImportError:
    print("❌ ecotaxa_py_client not installed!")
    print("\nInstall with:")
    print("  pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git")
    sys.exit(1)


def test_authentication(username: str, password: str) -> dict:
    """
    Test authentication with EcoTaxa API

    Args:
        username: EcoTaxa username
        password: EcoTaxa password

    Returns:
        dict with status and token (if successful)
    """
    print("🔐 Testing EcoTaxa Authentication...")
    print(f"   Username: {username}")
    print(f"   API Host: https://ecotaxa.obs-vlfr.fr/api")

    # Configure API client
    configuration = ecotaxa_py_client.Configuration(
        host="https://ecotaxa.obs-vlfr.fr/api"
    )

    try:
        with ecotaxa_py_client.ApiClient(configuration) as api_client:
            # Create authentication API instance
            auth_api = authentification_api.AuthentificationApi(api_client)

            # Create login request
            login_req = LoginReq(
                username=username,
                password=password
            )

            # Attempt login
            print("\n⏳ Attempting login...")
            response = auth_api.login(login_req)

            # Extract token
            access_token = response.get('token')

            if access_token:
                print("\n✅ Authentication Successful!")
                print(f"   Access Token: {access_token[:30]}...")
                print(f"   Token Length: {len(access_token)} characters")

                return {
                    'success': True,
                    'token': access_token,
                    'message': 'Authentication successful'
                }
            else:
                print("\n❌ Authentication Failed!")
                print("   No token received")
                return {
                    'success': False,
                    'token': None,
                    'message': 'No token in response'
                }

    except ecotaxa_py_client.ApiException as e:
        print(f"\n❌ API Error: {e}")
        print(f"   Status Code: {e.status}")
        print(f"   Reason: {e.reason}")
        return {
            'success': False,
            'token': None,
            'message': f'API Exception: {e.reason}'
        }

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return {
            'success': False,
            'token': None,
            'message': f'Error: {str(e)}'
        }


def save_token(token: str, filepath: str = '.ecotaxa_token'):
    """
    Save access token to file for later use

    Args:
        token: Access token string
        filepath: Path to save token
    """
    try:
        with open(filepath, 'w') as f:
            f.write(token)
        print(f"\n💾 Token saved to: {filepath}")
        print("   ⚠️  Keep this file secure! Don't commit to git.")
    except Exception as e:
        print(f"\n❌ Failed to save token: {e}")


def load_token(filepath: str = '.ecotaxa_token') -> str:
    """
    Load access token from file

    Args:
        filepath: Path to token file

    Returns:
        Access token string or None
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                token = f.read().strip()
            print(f"✅ Token loaded from: {filepath}")
            return token
        else:
            print(f"❌ Token file not found: {filepath}")
            return None
    except Exception as e:
        print(f"❌ Failed to load token: {e}")
        return None


def main():
    """Main function - interactive or programmatic usage"""

    print("=" * 60)
    print("EcoTaxa Authentication Test")
    print("=" * 60)

    # Option 1: Load credentials from environment variables (recommended)
    username = os.environ.get('ECOTAXA_USERNAME')
    password = os.environ.get('ECOTAXA_PASSWORD')

    if username and password:
        print("\n✓ Using credentials from environment variables")
    else:
        # Option 2: Interactive input
        print("\n📝 Enter your EcoTaxa credentials:")
        print("   (Get an account at https://ecotaxa.obs-vlfr.fr/)")
        username = input("   Username: ").strip()
        password = input("   Password: ").strip()

        if not username or not password:
            print("\n❌ Username and password are required!")
            sys.exit(1)

    # Test authentication
    result = test_authentication(username, password)

    if result['success']:
        # Save token for future use
        save_token(result['token'])

        print("\n" + "=" * 60)
        print("✅ TEST PASSED - You can now use EcoTaxa API!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run scripts/02_create_project.py to create a project")
        print("  2. Run scripts/03_upload_images.py to upload images")
        print("  3. Explore notebooks/01_ecotaxa_exploration.ipynb")

        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED - Check credentials and try again")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  • Verify your username and password at https://ecotaxa.obs-vlfr.fr/")
        print("  • Check your internet connection")
        print("  • Ensure your account is activated (check email)")

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
