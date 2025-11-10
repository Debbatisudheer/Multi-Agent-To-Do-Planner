from dataclasses import dataclass, field
from typing import Dict, List, Callable
import networkx as nx
from app.models import Task, Result

@dataclass
class DAG:
    g: nx.DiGraph = field(default_factory=nx.DiGraph)

    def add(self, task: Task):
        self.g.add_node(task.id, task=task)
        for dep in task.depends_on:
            self.g.add_edge(dep, task.id)

    def topo(self) -> List[str]:
        return list(nx.topological_sort(self.g))

class Executor:
    def __init__(self, dispatch: Callable[[Task], Result]):
        self.dispatch = dispatch

    def run(self, dag: DAG) -> Dict[str, Result]:
        results: Dict[str, Result] = {}
        for tid in dag.topo():
            if tid in results:
                continue
            task: Task = dag.g.nodes[tid]["task"]
            res = self.dispatch(task)
            results[tid] = res
            if res.status == "error":
                break
        return results
