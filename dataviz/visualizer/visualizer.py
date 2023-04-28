import json

class Visualizer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.nodes = []
        self.edges = []
        self.current_stage_id = -1

    def add_new_stage(self, title, content):
        self.current_stage_id += 1
        # # Replace newlines in content with &#xA; tags
        # content = content.replace("\n", "&#xA;")

        node = {
            "id": str(self.current_stage_id),
            "type": "custom",
            "position": {
                "x": 400 * (self.current_stage_id % 5),
                "y": 50 + 500 * (self.current_stage_id // 5)},
            "data": {"title": title, "content": content},
        }
        self.nodes.append(node)

        if self.current_stage_id > 1:
            edge = {
                "id": f"e{self.current_stage_id - 1}-{self.current_stage_id}",
                "source": str(self.current_stage_id - 1),
                "target": str(self.current_stage_id),
                "animated": True,
                "markerEnd": {"type": "arrowclosed"},
            }
            self.edges.append(edge)

        self._update_file()
        return self.current_stage_id

    def amend_stage(self, stage_id, title=None, content=None):
        # if content:
        #     # Replace newlines in content with &#xA; tags
        #     content = content.replace("\n", "&#xA;")

        for node in self.nodes:
            if node['id'] == str(stage_id):
                if title is not None:
                    node['data']['title'] = title
                if content is not None:
                    node['data']['content'] = content
                break

        self._update_file()

    def _update_file(self):
        data = {"nodes": self.nodes, "edges": self.edges}
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

