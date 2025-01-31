# faction/charts/faction.py


class FactionReportsChart:
    def __init__(self, data_source):
        """
        Initialize the chart with a data source.
        :param data_source: The data source to be used for rendering the chart.
        """
        self.data_source = data_source

    def render(self):
        """
        Render the chart configuration as a JSON-like dictionary.
        :return: A dictionary representing the chart configuration.
        """
        return {
            "type": "bar",
            "data": {
                "labels": [item["label"] for item in self.data_source],
                "datasets": [
                    {
                        "label": "Data",
                        "data": [item["count"] for item in self.data_source],
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "borderWidth": 1,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                    }
                },
            },
        }
