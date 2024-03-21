package main

import (
	"fmt"
	"math/bits"
	"runtime"
	"testing"
)

const JACK = 11

var INITIAL_STATE = NewState([4]int{13, 13, 13, 13}, 0, nil, nil)

type State struct {
	hash      int
	cardsLeft [4]int
	score     int
	parent    *State
	actions   *Stack
}

type Stack struct {
	value int
	prev  *Stack
}

func NewState(cardsLeft [4]int, score int, parent *State, actions *Stack) *State {
	state := new(State)
	state.hash = cardsLeft[0] + (cardsLeft[1]+(cardsLeft[2]+cardsLeft[3]*14)*14)*14
	state.cardsLeft = cardsLeft
	state.score = score
	state.parent = parent
	state.actions = actions
	return state
}

func (state *State) output() {

	actions := []int{}

	action := state.actions
	for action != nil {
		actions = append(actions, action.value+1)
		action = action.prev
	}

	fmt.Printf("Score: %v Actions: %v\n", state.score, actions)
	// for _, bonus := range this.bonuses {
	// 	fmt.Printf(" - %v", bonus)
	// }
	if state.parent != nil {
		state.parent.output()
	}
}

func processBatch(batch []*State, candidates chan *Table) {
	var best Table = map[int]*State{}

	for _, state := range batch {
		state.possibleStates(&best)
	}
	candidates <- &best
}

func (state *State) possibleStates(best *Table) {
	recursivePossibleStates(best, state, nil, state.score, 0, nil, state.cardsLeft)
}

func recursivePossibleStates(best *Table, parent *State, stack *Stack, score int, stackValue int, actions *Stack, cardsLeft [4]int) {
	endStack := true

	for action := range 4 {
		if cardsLeft[action] > 0 {
			card := layout[action][cardsLeft[action]-1]
			var cardValue int
			if card > 10 {
				cardValue = 10
			} else {
				cardValue = card
			}
			newStackValue := stackValue + cardValue
			if newStackValue <= 31 {
				endStack = false
				newStack := Stack{card, stack}
				newActions := Stack{action, actions}
				cardsLeft[action]--

				newScore := score

				if newStackValue == 15 || newStackValue == 31 {
					newScore += 2
				}

				if stack != nil && card == stack.value {
					if stack.prev != nil && card == stack.prev.value {
						if stack.prev.prev != nil && card == stack.prev.prev.value {
							newScore += 12
						} else {
							newScore += 6
						}
					} else {
						newScore += 2
					}
				}

				if stack == nil && card == JACK {
					newScore += 2
				}

				if stack != nil {
					straight := 3
					var mask uint = 1<<card | 1<<stack.value

					bestStraight := 0

					prevCard := stack.prev
					for prevCard != nil {
						mask |= 1 << prevCard.value
						ones := bits.OnesCount(mask)
						if ones == straight {
							lz := bits.LeadingZeros(mask)
							tz := bits.TrailingZeros(mask)
							if lz+tz+straight == bits.UintSize {
								bestStraight = straight
							}
						}
						straight++
						prevCard = prevCard.prev
					}

					newScore += bestStraight
				}

				recursivePossibleStates(best, parent, &newStack, newScore, newStackValue, &newActions, cardsLeft)

				cardsLeft[action]++
			}
		}
	}

	if endStack && actions != nil {
		candidate := NewState(cardsLeft, score, parent, actions)
		hash := candidate.hash
		contestant, exists := (*best)[hash]
		if !exists || contestant.score < candidate.score {
			(*best)[hash] = candidate
		}
	}
}

type Empty struct{}
type Set map[int]Empty
type Table map[int]*State

var queued = Empty{}

func solve() *State {
	best := map[int]*State{INITIAL_STATE.hash: INITIAL_STATE}
	queue := Set{INITIAL_STATE.hash: {}}

	candidates := make(chan *Table)

	for len(queue) > 0 {

		fmt.Println("Queue:", len(queue))
		nextQueue := Set{}
		active := 0
		batch := []*State{}
		for hash := range queue {
			state := best[hash]
			batch = append(batch, state)
			if len(batch) == 100 {
				go processBatch(batch, candidates)
				active++
				batch = []*State{}
			}
		}
		if len(batch) > 0 {
			go processBatch(batch, candidates)
			active++
		}

		added := 0
		replaced := 0
		for active > 0 {
			newTable := <-candidates
			active--

			for hash, candidate := range *newTable {
				contestant, exists := best[hash]
				if !exists || contestant.score < candidate.score {
					if exists {
						replaced++
					} else {
						added++
					}
					best[hash] = candidate
					nextQueue[hash] = queued
				}
			}
		}
		fmt.Printf("Added: %v Replaced: %v\n", added, replaced)

		queue = nextQueue
	}

	close(candidates)

	return best[0]
}

var layout = [4][13]int{
	{10, 9, 8, 2, 2, 7, 5, 1, 7, 4, 13, 2, 11},
	{6, 6, 1, 7, 4, 2, 9, 11, 12, 10, 8, 8, 10},
	{8, 3, 10, 6, 3, 13, 5, 12, 9, 5, 3, 13, 12},
	{7, 12, 1, 9, 6, 1, 4, 3, 4, 11, 11, 5, 13}}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	fmt.Println(runtime.NumCPU())

	myTest()

	// solve().output()

}

func myTest() {
	fn := func(b *testing.B) {
		for n := 0; n < b.N; n++ {
			solve().output()
		}
	}
	result := testing.Benchmark(fn)

	println(result.String())
}

func BenchmarkMain(b *testing.B) {
	fmt.Println("Starting benchmark", b.N)
	for i := 0; i < b.N; i++ {
		fmt.Println("Iteration", i)
		solve()
	}
}
