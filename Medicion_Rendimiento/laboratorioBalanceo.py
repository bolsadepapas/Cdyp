import multiprocessing as mp
import time
import math

# -----------------------------
# Configuracion del experimento
# -----------------------------
N_WORKERS = 4
N_TASKS = 80

# Las primeras tareas son mas costosas
TASKS = [
    (i, 240_000 if i < 20 else 30_000)
    for i in range(N_TASKS)
]


def process_task(task):
    """Simula una tarea intensiva en CPU."""
    task_id, cost = task
    result = 0.0

    for i in range(cost):
        result += math.sqrt((i % 997) + 1)

    return result


def worker(worker_id, mode, assigned, task_queue, result_queue):
    """Ejecuta las tareas asignadas al trabajador."""
    start = time.perf_counter()
    count = 0
    checksum = 0.0

    if mode == "dynamic":
        while True:
            task = task_queue.get()

            if task is None:
                break

            checksum += process_task(task)
            count += 1
    else:
        for task in assigned:
            checksum += process_task(task)
            count += 1

    elapsed = time.perf_counter() - start

    result_queue.put({
        "worker": worker_id,
        "tasks": count,
        "time": elapsed,
        "checksum": checksum
    })


def partition_block(tasks, workers):
    """Particionamiento estatico por bloques."""
    n = len(tasks)
    return [
        tasks[i * n // workers:(i + 1) * n // workers]
        for i in range(workers)
    ]


def partition_cyclic(tasks, workers):
    """Distribucion ciclica: una tarea por turno."""
    parts = [[] for _ in range(workers)]

    for i, task in enumerate(tasks):
        parts[i % workers].append(task)

    return parts


def run_parallel(mode, tasks, workers):
    task_queue = mp.Queue()
    result_queue = mp.Queue()

    if mode == "block":
        parts = partition_block(tasks, workers)
    elif mode == "cyclic":
        parts = partition_cyclic(tasks, workers)
    elif mode == "dynamic":
        parts = [[] for _ in range(workers)]

        # Preparar la cola compartida de tareas
        for task in tasks:
            task_queue.put(task)

        for _ in range(workers):
            task_queue.put(None)
    else:
        raise ValueError("Estrategia desconocida")

    processes = [
        mp.Process(
            target=worker,
            args=(i, mode, parts[i],
                  task_queue, result_queue)
        )
        for i in range(workers)
    ]

    start = time.perf_counter()

    for p in processes:
        p.start()

    results = []

    for _ in processes:
        results.append(result_queue.get())

    for p in processes:
        p.join()

    elapsed = time.perf_counter() - start

    if any(p.exitcode != 0 for p in processes):
        raise RuntimeError("Un trabajador fallo")

    return elapsed, sorted(results, key=lambda r: r["worker"])


def main():
    # Referencia secuencial
    start = time.perf_counter()
    sequential_checksum = sum(process_task(t) for t in TASKS)
    t_seq = time.perf_counter() - start

    print(f"Tiempo secuencial: {t_seq:.3f} s")
    print(f"Checksum secuencial: {sequential_checksum:.3f}")
    print()

    for mode in ("block", "cyclic", "dynamic"):
        elapsed, results = run_parallel(
            mode, TASKS, N_WORKERS
        )

        times = [r["time"] for r in results]
        mean_time = sum(times) / len(times)
        imbalance = (
            (max(times) - min(times)) / mean_time * 100
            if mean_time > 0 else 0
        )

        speedup = t_seq / elapsed
        efficiency = speedup / N_WORKERS * 100

        print(f"Estrategia: {mode}")
        print(f"Tiempo paralelo: {elapsed:.3f} s")
        print(f"Speedup: {speedup:.2f}")
        print(f"Eficiencia: {efficiency:.1f}%")
        print(f"Desequilibrio temporal: {imbalance:.1f}%")

        for r in results:
            print(
                f"  Trabajador {r['worker']}: "
                f"{r['tasks']} tareas, "
                f"{r['time']:.3f} s"
            )

        print()


if __name__ == "__main__":
    mp.freeze_support()
    main()