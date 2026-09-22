/**
 * This kernel function sums two arrays of integers and returns its result
 * through a third array.
 **/
__kernel void sumArrays(__global int* a, __global int* b, __global int* c){
    int index = get_global_id(0);
    int valA = a[index];
    int valB = b[index];

    // Realizar múltiples operaciones matemáticas por elemento
    for(int i = 0; i < 100; i++){
        valA = (valA * 3 + 1) % 10007;
        valB = (valB * 7 + 3) % 10007;
    }

    c[index] = valA + valB;
}