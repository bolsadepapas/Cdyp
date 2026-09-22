#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

long long contador = 0;
std::mutex mutex;

const int NUM_HILOS = 4;
const int INCREMENTOS = 1'000'000; // cada hilo incrementa 1 millón de veces

void incrementar_sin_mutex() {
  for (int i = 0; i < INCREMENTOS; i++) {
    contador++; // contador para la condicion de carrera
  }
}

void incrementar_con_mutex() {
  for (int i = 0; i < INCREMENTOS; i++) {
    std::lock_guard<std::mutex> lock(mutex);
    contador++;
  }
}

void lanzar_hilos(void (*funcion)()) {
  contador = 0; // reinicia el contador antes de cada prueba

  std::vector<std::thread> hilos;
  for (int i = 0; i < NUM_HILOS; i++) {
    hilos.emplace_back(funcion);
  }
  for (auto &t : hilos) {
    t.join();
  }
}

int main() {
  long long esperado = (long long)NUM_HILOS * INCREMENTOS;

  std::cout << "Prebas (condicion de carrera)\n";
  lanzar_hilos(incrementar_sin_mutex);
  std::cout << "  Esperado : " << esperado << "\n";
  std::cout << "  Obtenido : " << contador << "\n";
  if (contador != esperado) {
    std::cout << "Perdidos " << (esperado - contador) << " incrementos\n\n";
  } else {
    std::cout << "  (sin error esta vez, intenta de nuevo)\n\n";
  }

  std::cout << "Pruebas usando mutex\n";
  lanzar_hilos(incrementar_con_mutex);
  std::cout << "  Esperado : " << esperado << "\n";
  std::cout << "  Obtenido : " << contador << "\n";
  if (contador == esperado) {
    std::cout << "  Correcto, no hay condicion de carrera\n";
  } else {
    std::cout << "  Tenemos !\n";
  }

  return 0;
}