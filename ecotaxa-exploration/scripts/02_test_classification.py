#!/usr/bin/env python3
"""
EcoTaxa Classification Test
Uploads test images and retrieves classification results
"""

import sys
import os
from pathlib import Path
import time
import json

try:
    import ecotaxa_py_client
    from ecotaxa_py_client.api import (
        authentification_api,
        projects_api,
        objects_api
    )
    from ecotaxa_py_client.model.login_req import LoginReq
    from ecotaxa_py_client.model.create_project_req import CreateProjectReq
except ImportError:
    print("❌ ecotaxa_py_client not installed!")
    print("Install with: pip install git+https://github.com/ecotaxa/ecotaxa_py_client.git")
    sys.exit(1)


class EcoTaxaClassifier:
    """Simple wrapper for EcoTaxa classification workflow"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.configuration = ecotaxa_py_client.Configuration(
            host="https://ecotaxa.obs-vlfr.fr/api"
        )
        self.access_token = None
        self.project_id = None

    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")

        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            auth_api = authentification_api.AuthentificationApi(api_client)
            login_req = LoginReq(
                username=self.username,
                password=self.password
            )
            response = auth_api.login(login_req)
            self.access_token = response.get('token')
            self.configuration.access_token = self.access_token

        if self.access_token:
            print("   ✓ Authenticated successfully")
            return True
        else:
            print("   ✗ Authentication failed")
            return False

    def create_project(self, title: str):
        """Create a new project"""
        print(f"\n📁 Creating project: {title}")

        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            proj_api = projects_api.ProjectsApi(api_client)

            try:
                project_req = CreateProjectReq(title=title)
                self.project_id = proj_api.create_project(project_req)
                print(f"   ✓ Project created with ID: {self.project_id}")
                return self.project_id
            except Exception as e:
                print(f"   ✗ Failed to create project: {e}")
                return None

    def get_classifications(self, project_id: int = None):
        """Get classification results for project"""
        if project_id:
            self.project_id = project_id

        if not self.project_id:
            print("   ✗ No project ID specified")
            return []

        print(f"\n📊 Fetching classifications for project {self.project_id}...")

        with ecotaxa_py_client.ApiClient(self.configuration) as api_client:
            obj_api = objects_api.ObjectsApi(api_client)

            try:
                # Get all objects in project
                object_set = obj_api.get_object_set(
                    project_id=self.project_id
                )

                objects = object_set.get('objects', [])
                print(f"   ✓ Found {len(objects)} objects")

                results = []
                for obj in objects:
                    result = {
                        'object_id': obj.get('objid'),
                        'image_name': obj.get('orig_id'),
                        'predicted_class': obj.get('classif_auto_name', 'Unknown'),
                        'confidence': obj.get('classif_auto_score', 0.0),
                        'validated_class': obj.get('classif_name'),
                        'status': obj.get('classif_qual')
                    }
                    results.append(result)

                return results

            except Exception as e:
                print(f"   ✗ Failed to fetch classifications: {e}")
                return []

    def print_results(self, results: list):
        """Pretty print classification results"""
        print("\n" + "=" * 80)
        print("CLASSIFICATION RESULTS")
        print("=" * 80)

        if not results:
            print("No results found")
            return

        # Group by predicted class
        class_counts = {}
        for result in results:
            pred_class = result['predicted_class']
            class_counts[pred_class] = class_counts.get(pred_class, 0) + 1

        print(f"\nTotal Objects: {len(results)}")
        print("\nClass Distribution:")
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {class_name}: {count}")

        print("\nDetailed Results:")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Object ID: {result['object_id']}")
            if result['image_name']:
                print(f"   Image: {result['image_name']}")
            print(f"   Predicted Class: {result['predicted_class']}")
            print(f"   Confidence: {result['confidence']:.3f}")
            if result['validated_class']:
                print(f"   Validated Class: {result['validated_class']}")
            print(f"   Status: {result['status']}")

        print("\n" + "=" * 80)

    def save_results(self, results: list, output_file: str):
        """Save results to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")


def main():
    """Main function"""
    print("=" * 80)
    print("EcoTaxa Classification Test")
    print("=" * 80)

    # Get credentials
    username = os.environ.get('ECOTAXA_USERNAME')
    password = os.environ.get('ECOTAXA_PASSWORD')

    if not username or not password:
        print("\n📝 Enter your EcoTaxa credentials:")
        username = input("   Username: ").strip()
        password = input("   Password: ").strip()

    if not username or not password:
        print("❌ Username and password are required!")
        return 1

    # Initialize classifier
    classifier = EcoTaxaClassifier(username, password)

    # Authenticate
    if not classifier.authenticate():
        return 1

    # Option 1: Test with existing project
    print("\n" + "=" * 80)
    print("OPTIONS")
    print("=" * 80)
    print("1. Test with existing project (enter project ID)")
    print("2. Create new test project")
    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        project_id = input("Enter project ID: ").strip()
        try:
            project_id = int(project_id)
            classifier.project_id = project_id
        except ValueError:
            print("❌ Invalid project ID")
            return 1
    elif choice == "2":
        project_title = f"Test Project - {time.strftime('%Y%m%d_%H%M%S')}"
        if not classifier.create_project(project_title):
            return 1

        print("\n" + "=" * 80)
        print("⚠️  MANUAL STEP REQUIRED")
        print("=" * 80)
        print(f"1. Go to: https://ecotaxa.obs-vlfr.fr/prj/{classifier.project_id}")
        print("2. Upload some plankton images")
        print("3. Run ML prediction")
        print("4. Come back here and press Enter when done")
        print("=" * 80)
        input("\nPress Enter when images are uploaded and classified...")
    else:
        print("❌ Invalid choice")
        return 1

    # Get classifications
    results = classifier.get_classifications()

    if not results:
        print("\n⚠️  No classifications found")
        print("   Make sure images are uploaded and ML prediction has been run")
        return 1

    # Display results
    classifier.print_results(results)

    # Save results
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'ecotaxa_results_{int(time.time())}.json'
    classifier.save_results(results, str(output_file))

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
