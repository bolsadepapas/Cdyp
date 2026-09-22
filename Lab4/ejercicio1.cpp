#include <chrono>
#include <iostream>
#include <random>
#include <sstream>
#include <thread>

using namespace std;

// Función que ejecutará cada hilo
void ejecutarHilo(int numeroHilo, const string &mensaje) {

  // Generador de números aleatorios independiente para cada hilo
  random_device rd;
  // aqui el generador de retraso es un random (rd()) de entre 1 y 300 ms
  mt19937 generador(rd());
  uniform_int_distribution<int> distribucion(1, 300);

  // Obtener el ID del hilo actual
  stringstream ss;
  ss << this_thread::get_id();
  string idHilo = ss.str();

  cout << "[Hilo " << numeroHilo << "] "
       << "ID: " << idHilo << " - " << mensaje << endl;

  // Bucle de iteraciones
  for (int i = 1; i <= 10; i++) {

    cout << "[Hilo " << numeroHilo << "] "
         << "ID: " << idHilo << " - Iteración " << i << endl;

    int retraso = distribucion(generador);

    this_thread::sleep_for(chrono::milliseconds(retraso));
  }

  cout << "[Hilo " << numeroHilo << "] "
       << "Finalizado." << endl;
}

int main() {

  cout << "Iniciando tres hilos..." << endl << endl;

  // Crear tres hilos independientes
  thread hilo1(ejecutarHilo, 1, "Primer hilo.");

  thread hilo2(ejecutarHilo, 2, "Segundo hilo.");

  thread hilo3(ejecutarHilo, 3, "Tercer hilo.");

  // Esperar a que terminen los tres hilos
  hilo1.join();
  hilo2.join();
  hilo3.join();

  cout << endl;
  cout << "Todos los hilos han terminado." << endl;

  return 0;
}