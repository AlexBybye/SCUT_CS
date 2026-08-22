---
source_id: swarm-intelligence-006
course_id: swarm_intelligence
title: "群体智能"
original_file: "学科资料/群体智能/群体智能第一次作业（开源）/PSO算法解决KroA100实验代码/代码位置/群体智能.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# 群体智能

```cpp
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <string>
#include <cmath>
#include <limits>
#include <cstdlib>
#include <ctime>
#include<numeric>
#include <algorithm>
#include <chrono>
#include <random>

struct City {
    double x, y;
};

struct Particle {
    std::vector<int> tour; // ���ӱ�ʾ��·��
    std::vector<double> velocity; // �ٶ�
    std::vector<int> bestTour; // ���·��
    double bestDistance = std::numeric_limits<double>::max();
    double distance;
};

struct PSOParams {
    int numParticles;
    double w;
    double c1;
    double c2;
    int maxIterations;
};
//�������
double distance(const City& a, const City& b) {
    return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}
double totalDistance(const std::vector<int>& tour, const std::vector<City>& cities) {
    double sum = 0;
    for (size_t i = 0; i < tour.size(); ++i) {
        sum += distance(cities[tour[i]], cities[tour[(i + 1) % tour.size()]]);
    }
    return sum;
}
void initializeParticles(std::vector<Particle>& particles, const std::vector<City>& cities, const PSOParams& params) {
    std::random_device rd;
    std::mt19937 gen(rd());

    for (Particle& particle : particles) {
        particle.tour.resize(cities.size());
        particle.velocity.resize(cities.size(), 0);
        particle.bestTour = particle.tour;

        std::iota(particle.tour.begin(), particle.tour.end(), 0); // ��ʼ��Ϊ0��n-1
        std::shuffle(particle.tour.begin(), particle.tour.end(), gen); // ���ϴ��

        particle.distance = totalDistance(particle.tour, cities);
        if (particle.distance < particle.bestDistance) {
            particle.bestDistance = particle.distance;
            particle.bestTour = particle.tour;
        }
    }
}
//������Ϣ
void updateVelocityAndPosition(std::vector<Particle>& particles, const PSOParams& params, const Particle& globalBest, const std::vector<City>& cities) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);

    for (Particle& particle : particles) {
        for (size_t i = 0; i < particle.tour.size(); ++i) {
            int city1 = particle.tour[i];
            int city2 = particle.bestTour[i];
            int globalCity = globalBest.bestTour[i];

            double r1 = dis(gen);
            double r2 = dis(gen);

            particle.velocity[i] = params.w * particle.velocity[i] +
                params.c1 * r1 * (city2 - city1) +
                params.c2 * r2 * (globalCity - city1);
        }

        // ����·��
        for (size_t i = 0; i < particle.tour.size(); ++i) {
            int nextCity = particle.tour[i] + static_cast<int>(particle.velocity[i]);
            particle.tour[i] = (nextCity + particle.tour.size()) % particle.tour.size();
        }

        particle.distance = totalDistance(particle.tour, cities);
        if (particle.distance < particle.bestDistance) {
            particle.bestDistance = particle.distance;
            particle.bestTour = particle.tour;
        }
    }
}
//���ļ��Ľӿ�
void loadCities(const std::string& filename, std::vector<City>& cities) {
    std::ifstream file(filename);
    std::string line;

    if (file.is_open()) {
        getline(file, line); // ���Ե�һ��
        while (getline(file, line)) {
            std::istringstream iss(line);
            City city;
            iss >> city.x >> city.y;
            cities.push_back(city);
        }
        file.close();
    }
    else {
        std::cerr << "Unable to open file: " << filename << std::endl;
    }
}

int main() {
    std::vector<City> cities;
    loadCities("kroA100.tsp", cities);

    if (cities.empty()) {
        std::cerr << "Failed to load cities." << std::endl;
        return 1;
    }

    PSOParams params = { 115, 0.6, 2.6, 1.4, 100000 };
    std::vector<Particle> particles(params.numParticles);

    initializeParticles(particles, cities, params);
    Particle globalBest = particles[0];
    globalBest.bestDistance = std::numeric_limits<double>::max();

    // ���ļ�����д��
    std::ofstream outFile("pso_results.txt");
    if (!outFile.is_open()) {
        std::cerr << "Failed to open file for writing." << std::endl;
        return 1;
    }

    // ��ȡ��ʼʱ���
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < params.maxIterations; ++i) {
        bool globalBestUpdated = false;
        for (Particle& particle : particles) {
            if (particle.bestDistance < globalBest.bestDistance) {
                globalBest = particle;
                globalBestUpdated = true;
            }
        }

        if (globalBestUpdated) {
            std::cout << "Iteration " << i << ": Best distance improved to " << globalBest.bestDistance << std::endl;
            outFile  << globalBest.bestDistance << std::endl;
        }
        else {
            std::cout << "Iteration " << i << ": Best distance unchanged at " << globalBest.bestDistance << std::endl;
            outFile << globalBest.bestDistance << std::endl;
        }

        updateVelocityAndPosition(particles, params, globalBest, cities);
    }

    std::cout << "Final best distance: " << globalBest.bestDistance << std::endl;
    outFile << "Final best distance: " << globalBest.bestDistance << std::endl;

    // ��ȡ����ʱ���
    auto end = std::chrono::high_resolution_clock::now();
    // �������ʱ��
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Time elapsed: " << elapsed.count() << " s" << std::endl;
    outFile << "Time elapsed: " << elapsed.count() << " s" << std::endl;

    // �ر��ļ�
    outFile.close();

    return 0;
}
```
