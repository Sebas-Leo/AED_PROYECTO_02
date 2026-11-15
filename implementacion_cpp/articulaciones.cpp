#include <algorithm>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// Implementacion propia. No se usa una biblioteca de algoritmos de grafos.
// Cada arista tiene identidad: se omite SOLO la arista del padre, lo que
// permite manejar tambien aristas paralelas y lazos correctamente.
struct Solver {
    int n, timer=0; bool trace; ostream& out;
    vector<pair<int,int>> edges;
    vector<vector<pair<int,int>>> adj;
    vector<int> tin, low, parent, cut;
    Solver(int n, vector<pair<int,int>> es, bool t, ostream& o):
        n(n),trace(t),out(o),edges(es),adj(n),tin(n,-1),low(n,-1),parent(n,-1),cut(n,0) {
        for(int i=0;i<(int)edges.size();++i){auto [u,v]=edges[i];adj[u].push_back({v,i});adj[v].push_back({u,i});}
    }
    void arr(const vector<int>& a){out<<'[';for(int i=0;i<(int)a.size();++i){if(i)out<<',';out<<a[i];}out<<']';}
    void emit(string kind,int v,int to=-1){
        if(!trace)return;
        out<<"{\"kind\":\""<<kind<<"\",\"v\":"<<v<<",\"to\":"<<to<<",\"tin\":";arr(tin);
        out<<",\"low\":";arr(low);out<<",\"parent\":";arr(parent);out<<",\"cut\":";arr(cut);out<<"}\n";
    }
    void dfs(int v,int parentEdge=-1){
        // Descubrir: cada vertice recibe un tiempo unico y creciente.
        tin[v]=low[v]=timer++; int children=0; emit("discover",v);
        for(auto [to,id]:adj[v]){
            if(id==parentEdge)continue;
            // Arista a visitado: se toma SU tin, no su low.
            if(tin[to]!=-1){low[v]=min(low[v],tin[to]);emit("back",v,to);}
            else {
                parent[to]=v;emit("tree",v,to);dfs(to,id);++children;
                // Al volver del hijo, propagamos lo que alcanza su subarbol.
                low[v]=min(low[v],low[to]);emit("return",v,to);
                // Incluye igualdad: volver a v no permite evitar v.
                if(parentEdge!=-1 && low[to]>=tin[v]){cut[v]=1;emit("cut",v,to);}
            }
        }
        // La raiz requiere una regla distinta: contar hijos DFS, no vecinos.
        if(parentEdge==-1){if(children>1)cut[v]=1;emit("root",v,children);}
        emit("finish",v);
    }
    void run(){for(int v=0;v<n;++v)if(tin[v]==-1)dfs(v);emit("result",-1);}
};
int main(int argc,char** argv){
    bool trace=argc>1 && string(argv[1])=="--trace";
    int n,m;if(!(cin>>n>>m)||n<0||m<0){cerr<<"Entrada: n m y luego m pares u v (indices desde 0).\n";return 1;}
    vector<pair<int,int>> es;
    for(int i=0;i<m;++i){int u,v;if(!(cin>>u>>v)||u<0||v<0||u>=n||v>=n){cerr<<"Arista invalida\n";return 1;}es.push_back({u,v});}
    Solver s(n,es,trace,cout);s.run();
    if(!trace){bool first=true;for(int i=0;i<n;++i)if(s.cut[i]){if(!first)cout<<' ';cout<<i;first=false;}cout<<'\n';}
}
