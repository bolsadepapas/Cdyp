import multiprocessing as mp
import time
import math

# -----------------------------
# Configuracion del experimento
# -----------------------------
WORKERS_LIST = [1, 2, 4, 8]
N_TASKS = 80

# Las primeras tareas son mas costosas (asimetria de carga)
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
        for task in tasks:
            task_queue.put(task)
        for _ in range(workers):
            task_queue.put(None)
    else:
        raise ValueError("Estrategia desconocida")

    processes = [
        mp.Process(
            target=worker,
            args=(i, mode, parts[i], task_queue, result_queue)
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
    print("=" * 65)
    print("  EXPERIMENTO DE BALANCEO DE CARGA Y SPEEDUP (1, 2, 4, 8 WORKERS)")
    print("=" * 65)

    # Referencia secuencial
    start = time.perf_counter()
    sequential_checksum = sum(process_task(t) for t in TASKS)
    t_seq = time.perf_counter() - start

    print(f"Tiempo secuencial base: {t_seq:.3f} s")
    print(f"Checksum secuencial:   {sequential_checksum:.3f}\n")

    summary_table = []

    for n_workers in WORKERS_LIST:
        print(f"\n{'#' * 65}")
        print(f"--- PRUEBA CON {n_workers} TRABAJADOR(ES) ---")
        print(f"{'#' * 65}\n")

        for mode in ("block", "cyclic", "dynamic"):
            elapsed, results = run_parallel(mode, TASKS, n_workers)

            times = [r["time"] for r in results]
            mean_time = sum(times) / len(times)
            imbalance = (
                (max(times) - min(times)) / mean_time * 100
                if mean_time > 0 else 0
            )

            speedup = t_seq / elapsed
            efficiency = speedup / n_workers * 100

            summary_table.append({
                "workers": n_workers,
                "mode": mode,
                "elapsed": elapsed,
                "speedup": speedup,
                "efficiency": efficiency,
                "imbalance": imbalance
            })

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
            print("-" * 45)

    # Resumen comparativo final
    print("\n" + "=" * 70)
    print("RESUMEN COMPARATIVO DE SPEEDUP Y EFICIENCIA")
    print("=" * 70)
    print(f"{'Workers':<8}{'Modo':<10}{'Tiempo (s)':<14}{'Speedup':<12}{'Eficiencia':<14}{'Desequilibrio':<12}")
    print("-" * 70)
    for row in summary_table:
        print(
            f"{row['workers']:<8}{row['mode']:<10}{row['elapsed']:<14.3f}"
            f"{row['speedup']:<12.2f}{row['efficiency']:<13.1f}%"
            f"{row['imbalance']:<11.1f}%"
        )
    print("=" * 70)


if __name__ == "__main__":
    mp.freeze_support()
    main()
