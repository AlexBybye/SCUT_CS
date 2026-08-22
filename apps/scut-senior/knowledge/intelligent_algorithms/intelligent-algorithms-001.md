---
source_id: intelligent-algorithms-001
course_id: intelligent_algorithms
title: CVRP
original_file: "学科资料/智能算法/智能算法竞赛/CVRP.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# CVRP

```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <climits>
#include <ctime>
using namespace std;

struct Node {
    int x, y;
};

vector<Node> nodes;
vector<int> demand;
int capacity;
int dimension;
int depot;
int best_value;

int get_distance(int i, int j) {
    double dx = nodes[i].x - nodes[j].x;
    double dy = nodes[i].y - nodes[j].y;
    return (int)(sqrt(dx*dx + dy*dy));
}

void read_input(const string &filename) {
    ifstream file;
    file.open(filename);
    string line;
    while (getline(file, line)) {
        if (line.find("DIMENSION") != string::npos) {
            istringstream iss(line);
            string tmp;
            iss >> tmp >> tmp >> dimension;
        }
        else if (!best_value && line.find("COMMENT") != string::npos) {
            //std::cout << "aaa" << '\n';
            istringstream iss(line);
            string tmp;
            iss >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp >> tmp;
            //std::cout << tmp << '\n';
            int i = 0;
            while(tmp[i] >= '0' && tmp[i] <= '9')
            {
                best_value = best_value * 10 + (tmp[i] - '0');
                i++;
            }
            
        }
        else if (line.find("CAPACITY") != string::npos) {
            istringstream iss(line);
            string tmp;
            iss >> tmp >> tmp >> capacity;
        }
        else if (line.find("NODE_COORD_SECTION") != string::npos) {
            nodes.resize(dimension);
            for (int i = 0; i < dimension; ++i) {
                while (getline(file, line) && line.empty());
                istringstream iss(line);
                int s, x, y;
                iss >> s >> x >> y;
                nodes[s-1].x = x;
                nodes[s-1].y = y;
            }
        } else if (line.find("DEMAND_SECTION") != string::npos) {
            demand.resize(dimension);
            for (int i = 0; i < dimension; ++i) {
                while (getline(file, line) && line.empty());
                istringstream iss(line);
                int s, d;
                iss >> s >> d;
                demand[s-1] = d;
            }
        }  else if (line.find("DEPOT_SECTION") != string::npos) {
            while (getline(file, line) && line.empty());
            istringstream iss(line);
            int s;
            iss >> s;
            if (s < 1 || s > dimension) {
                cerr << "Error: Depot number " << s << " is out of range [1, " << dimension << "]" << endl;
                exit(1);
            }
            depot = s - 1;
        }
    }
    // 验证 nodes 和 demand 的大小
    if (nodes.size() != dimension || demand.size() != dimension) {
        cerr << "Error: nodes.size() = " << nodes.size() 
             << ", demand.size() = " << demand.size() 
             << ", but dimension is " << dimension << endl;
        exit(1);
    }
}

int main() {
    srand(time(0));
    int T = 25;
    int MAX_GBL = 9999999;
    int SUM_GBL = 0;
    //std::cout << best_value << '\n';
    while(T--)
    {
        read_input("C:/Users/24441/Desktop/A/A-n34-k5.vrp");//请在这里输入文件名，建议直接复制文件路径
        std::cout << 25-T << '\n';
        //std::cout << capacity << '\n';
        // for(auto i : nodes)
        // {
        //     std::cout << i.x << i.y << '\n';
        // }

        const double alpha = 1.0;
        const double beta = 5.0;
        const double rho = 0.3;
        const double Q = 50.0;
        const int max_iterations = 300;
        const int num_ants = 50;
        const double initial_tau = 1.0;

        vector<vector<double>> tau(dimension, vector<double>(dimension, initial_tau));
        double global_best_length = 1e18;
        vector<vector<int>> global_best_routes;

        for (int iter = 0; iter < max_iterations; ++iter) {
            vector<vector<vector<int>>> all_ant_routes(num_ants);

            for (int ant = 0; ant < num_ants; ++ant) {
                vector<bool> visited(dimension, false);
                visited[depot] = true;
                for (int i = 0; i < dimension; ++i)
                    if (demand[i] == 0) visited[i] = true;

                vector<vector<int>> routes;
                int current_node = depot;
                int current_cap = capacity;
                vector<int> current_route;

                while (true) {
                    vector<int> candidates;
                    for (int i = 0; i < dimension; ++i)
                        if (!visited[i] && demand[i] <= current_cap)
                            candidates.push_back(i);

                    if (candidates.empty()) {
                        if (!current_route.empty()) {
                            routes.push_back(current_route);
                            current_route.clear();
                            current_cap = capacity;
                            current_node = depot;
                        } else break;
                    } else {
                        vector<double> probs;
                        double sum = 0.0;
                        for (int j : candidates) {
                            double pheromone = tau[current_node][j];
                            double eta = 1.0 / get_distance(current_node, j);
                            double p = pow(pheromone, alpha) * pow(eta, beta);
                            sum += p;
                            probs.push_back(p);
                        }

                        if (sum == 0) {
                            int selected = candidates[rand() % candidates.size()];
                            current_route.push_back(selected);
                            visited[selected] = true;
                            current_cap -= demand[selected];
                            current_node = selected;
                        } else {
                            for (double &p : probs) p /= sum;
                            double r = (double)rand() / RAND_MAX;
                            double s = 0.0;
                            int selected = candidates.back();
                            for (int i = 0; i < (int)candidates.size(); ++i) {
                                s += probs[i];
                                if (r <= s) {
                                    selected = candidates[i];
                                    break;
                                }
                            }
                            current_route.push_back(selected);
                            visited[selected] = true;
                            current_cap -= demand[selected];
                            current_node = selected;
                        }
                    }

                    bool all_visited = true;
                    for (int i = 0; i < dimension; ++i)
                        if (!visited[i] && demand[i] > 0) {
                            all_visited = false;
                            break;
                        }
                    if (all_visited) {
                        if (!current_route.empty()) routes.push_back(current_route);
                        break;
                    }
                }
                all_ant_routes[ant] = routes;
            }

            double iter_best = 1e18;
            vector<vector<int>> iter_routes;
            for (auto &routes : all_ant_routes) {
                double len = 0;
                for (auto &route : routes) {
                    if (route.empty()) continue;
                    int prev = depot;
                    for (int node : route) {
                        len += get_distance(prev, node);
                        prev = node;
                    }
                    len += get_distance(prev, depot);
                }
                if (len < iter_best) {
                    iter_best = len;
                    iter_routes = routes;
                }
            }

            if (iter_best < global_best_length) {
                global_best_length = iter_best;
                global_best_routes = iter_routes;
            }

            for (int i = 0; i < dimension; ++i)
                for (int j = 0; j < dimension; ++j)
                    tau[i][j] *= (1 - rho);

            for (auto &route : iter_routes) {
                if (route.empty()) continue;
                int prev = depot;
                for (int node : route) {
                    tau[prev][node] += Q / iter_best;
                    tau[node][prev] += Q / iter_best;
                    prev = node;
                }
                tau[prev][depot] += Q / iter_best;
                tau[depot][prev] += Q / iter_best;
            }
        }

        int route_num = 1;
        for (auto &route : global_best_routes) {
            std::cout << "Route #" << route_num++ << ": ";
            for (size_t i = 0; i < route.size(); ++i) {
                if (i > 0) cout << " ";
                std::cout << (route[i] + 1);
            }
            std::cout << endl;
        }
        std::cout << "Cost " << global_best_length << endl;

        MAX_GBL = MAX_GBL < global_best_length ? MAX_GBL : global_best_length;
        SUM_GBL += global_best_length;
    }

    best_value *= 25;
    //std::cout << "aaa" << SUM_GBL << "bbb" << best_value << '\n';
    std::cout << "\n\n";
    std::cout << MAX_GBL << '\n' << (SUM_GBL - best_value)*100.0/best_value << '\n';

    return 0;
}
```
