from collections import Counter, defaultdict
import heapq
from .density import external_edges
from .models import ClusterState
from .partitioning import PartitioningCliqueClusterer

class OptimizedPartitioningCliqueClusterer(PartitioningCliqueClusterer):
    """Indexed backend preserving the locked IEEE-methodology result order."""
    def fit(self, graph):
        self._neighbor_position={(u,v):i for u in graph.nodes() for i,v in enumerate(graph.neighbors(u))}
        return super().fit(graph)
    def _orientation(self,e,s):
        a,b=tuple(e); first=min((n for n in (a,b) if n in s.nodes),key=self.node_order.__getitem__); other=b if a==first else a
        return first,other,(self.node_order[first],self._neighbor_position[(first,other)])
    def _edge_degree(self,e):
        u,v=tuple(e); return self.node_degrees[u]+self.node_degrees[v]-1
    def _index_add(self,e,s):
        if e in self._active:self._index_refresh(e,s);return
        d=self._edge_degree(e); key=self._orientation(e,s)[2]; self._active.add(e); self._counts[d]+=1; self._degree_sum+=d; heapq.heappush(self._heaps[d],(key,e))
    def _index_refresh(self,e,s):
        if e in self._active:heapq.heappush(self._heaps[self._edge_degree(e)],(self._orientation(e,s)[2],e))
    def _index_remove(self,e):
        if e in self._active:
            self._active.remove(e); d=self._edge_degree(e); self._counts[d]-=1; self._degree_sum-=d
            if not self._counts[d]:del self._counts[d]
    def _build_edge_index(self,s,forbidden):
        self._active=set(); self._counts=Counter(); self._degree_sum=0; self._heaps=defaultdict(list)
        for e in s.external_edges:
            if e.isdisjoint(forbidden):self._index_add(e,s)
    def _next_single_edge(self,s,forbidden):
        if self.trace:return super()._next_single_edge(s,forbidden)
        if not self._active:return None
        avg=int(self._degree_sum/len(self._active)); degrees=sorted(self._counts)
        if avg in self._counts:selected=avg
        else:
            lower=max((d for d in degrees if d<avg),default=None); upper=min((d for d in degrees if d>avg),default=None)
            selected=upper if lower is None else lower if upper is None else upper if abs(lower-avg)>=abs(upper-avg) else lower
        heap=self._heaps[selected]
        while heap:
            key,e=heap[0]
            if e not in self._active or key!=self._orientation(e,s)[2]:heapq.heappop(heap);continue
            return e
        raise RuntimeError("Edge index inconsistent")
    def _add_triangle_candidates(self,nodes,available,used,forbidden):
        for n in nodes:self._triangle_candidates.update(t for t in self.node_to_triangles.get(n,()) if t in available and t not in used and set(t).isdisjoint(forbidden))
    def _next_triangle(self,s,available,forbidden):
        grouped={3:[],2:[],1:[]}
        for t in sorted(self._triangle_candidates,key=self.triangle_order.__getitem__):
            common=len(set(t)&s.nodes)
            if common in grouped:grouped[common].append(t)
        for common in (3,2,1):
            if grouped[common]:return self._select_triangle(grouped[common])
        return None
    def _update_state(self,s,new_nodes,new_edges,forbidden):
        for e in new_edges:self._index_remove(e)
        s.nodes.update(new_nodes);s.internal_edges.update(new_edges);s.external_edges.difference_update(new_edges)
        for n in new_nodes:
            for v in self.graph.neighbors(n):
                e=frozenset((n,v))
                if e not in s.internal_edges:
                    s.external_edges.add(e)
                    if e.isdisjoint(forbidden):self._index_add(e,s)
            for v in self.graph.neighbors(n):self._index_refresh(frozenset((n,v)),s)
        den=len(s.internal_edges)+len(s.external_edges);s.relative_density=round(len(s.internal_edges)/den if den else 0,2)
    def _expand_cluster(self,seed,available_triangles,forbidden):
        s=ClusterState(set(seed),set(self.triangle_edge_map[seed]),{seed},0.0);s.external_edges=external_edges(self.graph,s.nodes,s.internal_edges)
        den=len(s.internal_edges)+len(s.external_edges);s.relative_density=round(len(s.internal_edges)/den if den else 0,2)
        self._build_edge_index(s,forbidden);available=set(available_triangles);self._triangle_candidates=set();self._add_triangle_candidates(s.nodes,available,s.used_triangles,forbidden);self._triangle_candidates.discard(seed)
        best=s.copy();best_difference=abs(s.relative_density-self.target_density)
        while s.relative_density!=self.target_density:
            triangle=self._next_triangle(s,available,forbidden)
            if triangle is not None:
                new_nodes=set(triangle)-s.nodes;new_edges=self.triangle_edge_map[triangle]-s.internal_edges;s.used_triangles.add(triangle);self._triangle_candidates.discard(triangle);self._add_triangle_candidates(new_nodes,available,s.used_triangles,forbidden);self._update_state(s,new_nodes,new_edges,forbidden)
            else:
                edge=self._next_single_edge(s,forbidden)
                if edge is None:break
                new_nodes=set(edge)-s.nodes;self._add_triangle_candidates(new_nodes,available,s.used_triangles,forbidden);self._update_state(s,new_nodes,{edge},forbidden)
            difference=abs(s.relative_density-self.target_density)
            if difference<best_difference:best=s.copy();best_difference=difference
        return s.copy() if s.relative_density==self.target_density else best


# Backward-compatible class alias for scripts created before v1.0.1.
ScalablePartitioningCliqueClusterer = OptimizedPartitioningCliqueClusterer
