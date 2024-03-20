package main

import (
	"fmt"
	"testing"
)

func BenchmarkSolver(b *testing.B) {
	fmt.Println("Starting benchmark", b.N)
	for i := 0; i < b.N; i++ {
		fmt.Println("Iteration", i)
		main()
	}
}
