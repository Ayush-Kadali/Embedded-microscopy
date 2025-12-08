"""
Module 7: Export & Reporting

Responsibility: Persist results and generate reports.
"""

from typing import Dict, Any, List
import csv
import json
import os
from pathlib import Path
from datetime import datetime
from .base import PipelineModule


class ExportModule(PipelineModule):
    """
    Exports results to CSV and optionally generates dashboard.

    Input Contract:
        - metadata: dict (from acquisition)
        - counts_by_class: dict[str, int]
        - organisms: list of dict
        - diversity_indices: dict
        - bloom_alerts: list of dict
        - export_config: dict with output_dir, generate_dashboard, etc.

    Output Contract:
        - status: str
        - error_message: str | None
        - csv_path: str
        - dashboard_url: str | None
        - exported_files: list of str
    """

    def validate_config(self) -> None:
        """Validate export configuration."""
        if 'output_dir' not in self.config:
            self.config['output_dir'] = './results'

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        required = ['metadata', 'counts_by_class', 'organisms', 'diversity_indices', 'bloom_alerts']
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export results to files."""
        try:
            metadata = input_data['metadata']
            counts_by_class = input_data['counts_by_class']
            organisms = input_data['organisms']
            diversity_indices = input_data['diversity_indices']
            bloom_alerts = input_data['bloom_alerts']
            config = input_data.get('export_config', self.config)

            output_dir = config.get('output_dir', './results')
            export_images = config.get('export_images', False)
            generate_dashboard = config.get('generate_dashboard', False)

            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            exported_files = []

            # 1. Export summary CSV
            csv_path = self._export_summary_csv(
                output_dir, metadata, counts_by_class, diversity_indices, bloom_alerts
            )
            exported_files.append(csv_path)

            # 2. Export detailed organism data
            detailed_path = self._export_detailed_csv(output_dir, metadata, organisms)
            exported_files.append(detailed_path)

            # 3. Export JSON metadata
            json_path = self._export_json(
                output_dir, metadata, counts_by_class, organisms, diversity_indices, bloom_alerts
            )
            exported_files.append(json_path)

            # 4. Generate dashboard (if requested)
            dashboard_url = None
            if generate_dashboard:
                dashboard_url = self._generate_dashboard_stub(output_dir)

            self.logger.info(f"Export complete: {len(exported_files)} files written to {output_dir}")

            return {
                'status': 'success',
                'error_message': None,
                'csv_path': csv_path,
                'dashboard_url': dashboard_url,
                'exported_files': exported_files,
            }

        except Exception as e:
            return self.handle_error(e)

    def _export_summary_csv(
        self,
        output_dir: str,
        metadata: Dict,
        counts_by_class: Dict[str, int],
        diversity_indices: Dict,
        bloom_alerts: List[Dict]
    ) -> str:
        """
        Export summary CSV with one row per class.

        Format: sample_id, timestamp, gps_lat, gps_lon, magnification,
                class_name, count, mean_size_um, shannon_diversity, bloom_alert
        """
        capture_id = metadata.get('capture_id', 'unknown')
        timestamp = metadata.get('timestamp', datetime.now().isoformat())
        gps_coords = metadata.get('gps_coordinates', [None, None])
        magnification = metadata.get('magnification', 0)
        shannon = diversity_indices.get('shannon', 0)

        # Create bloom alert lookup
        bloom_lookup = {alert['class_name']: True for alert in bloom_alerts}

        # Write CSV
        csv_path = os.path.join(output_dir, f'summary_{capture_id}.csv')

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'sample_id', 'timestamp', 'gps_lat', 'gps_lon', 'magnification',
                'class_name', 'count', 'shannon_diversity', 'bloom_alert'
            ])

            # Data rows (one per class)
            for class_name, count in counts_by_class.items():
                writer.writerow([
                    capture_id,
                    timestamp,
                    gps_coords[0] if gps_coords else None,
                    gps_coords[1] if gps_coords else None,
                    magnification,
                    class_name,
                    count,
                    f"{shannon:.3f}",
                    bloom_lookup.get(class_name, False),
                ])

        return csv_path

    def _export_detailed_csv(
        self,
        output_dir: str,
        metadata: Dict,
        organisms: List[Dict]
    ) -> str:
        """Export detailed organism-level data."""
        capture_id = metadata.get('capture_id', 'unknown')
        csv_path = os.path.join(output_dir, f'organisms_{capture_id}.csv')

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'sample_id', 'organism_id', 'class_name', 'confidence',
                'size_um', 'centroid_x_px', 'centroid_y_px',
                'centroid_x_um', 'centroid_y_um'
            ])

            # Data rows
            for org in organisms:
                writer.writerow([
                    capture_id,
                    org['organism_id'],
                    org['class_name'],
                    f"{org['confidence']:.3f}",
                    f"{org['size_um']:.2f}",
                    org['centroid_px'][0],
                    org['centroid_px'][1],
                    f"{org['centroid_um'][0]:.2f}",
                    f"{org['centroid_um'][1]:.2f}",
                ])

        return csv_path

    def _export_json(
        self,
        output_dir: str,
        metadata: Dict,
        counts_by_class: Dict,
        organisms: List[Dict],
        diversity_indices: Dict,
        bloom_alerts: List[Dict]
    ) -> str:
        """Export complete results as JSON."""
        capture_id = metadata.get('capture_id', 'unknown')
        json_path = os.path.join(output_dir, f'results_{capture_id}.json')

        # Build complete result object
        results = {
            'metadata': metadata,
            'counts_by_class': counts_by_class,
            'diversity_indices': diversity_indices,
            'bloom_alerts': bloom_alerts,
            'organisms': organisms,
        }

        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)

        return json_path

    def _generate_dashboard_stub(self, output_dir: str) -> str:
        """
        Stub for dashboard generation.

        In production, implement with:
            - Streamlit: Create app.py that reads CSV files
            - Folium: Generate interactive maps from GPS data
            - Plotly: Create interactive plots

        For now, just return a placeholder URL.
        """
        # STUB: In production, launch Streamlit server
        # streamlit run dashboard/app.py --server.port 8501

        dashboard_path = os.path.join(output_dir, 'dashboard.html')

        # Create minimal HTML dashboard stub
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Plankton Analysis Dashboard</title></head>
        <body>
            <h1>Marine Plankton Analysis Dashboard</h1>
            <p>Dashboard stub - replace with Streamlit/Folium implementation</p>
            <p>Check the CSV files for detailed results.</p>
        </body>
        </html>
        """

        with open(dashboard_path, 'w') as f:
            f.write(html_content)

        return f"file://{os.path.abspath(dashboard_path)}"
