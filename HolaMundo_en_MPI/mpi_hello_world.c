#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
  // Inicializar el entorno MPI
  MPI_Init(NULL, NULL);

  // Obtener el número de procesos
  int world_size;
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);

  // Obtener el rango (rank) del proceso actual
  int world_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  // Obtener el nombre del procesador/host
  char processor_name[MPI_MAX_PROCESSOR_NAME];
  int name_len;
  MPI_Get_processor_name(processor_name, &name_len);

  // Imprimir mensaje de Hello Worldc
  printf("Hello world from processor %s, rank %d out of %d processors\n",
         processor_name, world_rank, world_size);

  // Finalizar el entorno MPI
  MPI_Finalize();
  return 0;
}