package main

import (
	"bufio"
	"fmt"
	"math/bits"
	"os"
	"runtime"
	"strconv"
	"strings"
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
	if state.parent != nil {
		state.parent.output()
	}
}

var START_X = 1250
var START_Y = 225
var DX_PER_ACTION = 371
var DY_PER_CARD = 72
var STACK_X = 810
var STACK_START_Y = 612

func (state *State) outputAHK() {

	if state.parent != nil {
		state.parent.outputAHK()
	}

	stackSize := 0
	action := state.actions
	cardsLeft := state.cardsLeft
	for action != nil {
		// click card
		x := action.value*DX_PER_ACTION + START_X
		y := cardsLeft[action.value]*DY_PER_CARD + START_Y
		fmt.Printf("MyClick %v, %v\n", x, y)
		cardsLeft[action.value]--
		action = action.prev
		stackSize++
	}

	// next stack
	fmt.Printf("MyClick %v, %v\n", STACK_X, STACK_START_Y-DY_PER_CARD*stackSize)
}

func createAHK(state *State) {
	fmt.Println("#Requires AutoHotkey v2.0")
	fmt.Println("#SingleInstance Force")
	fmt.Println("SendMode \"Event\"")
	fmt.Println("Scrolllock::")
	fmt.Println("{")
	state.outputAHK()
	fmt.Println("}")

	fmt.Println("MyClick(x, y)")
	fmt.Println("{")
	fmt.Println("MouseMove x, y")
	fmt.Println("Click \"Down\"")
	fmt.Println("Sleep 60")
	fmt.Println("Click \"Up\"")
	fmt.Println("Sleep 60")
	fmt.Println("}")
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
		queue = nextQueue
	}

	close(candidates)

	return best[0]
}

// var layout = [4][13]int{
// 	{10, 9, 8, 2, 2, 7, 5, 1, 7, 4, 13, 2, 11},
// 	{6, 6, 1, 7, 4, 2, 9, 11, 12, 10, 8, 8, 10},
// 	{8, 3, 10, 6, 3, 13, 5, 12, 9, 5, 3, 13, 12},
// 	{7, 12, 1, 9, 6, 1, 4, 3, 4, 11, 11, 5, 13}}

var layout = [4][13]int{
	{2, 1, 13, 2, 2, 12, 3, 4, 5, 11, 5, 3, 9},
	{6, 10, 13, 3, 1, 13, 12, 7, 6, 9, 8, 3, 7},
	{12, 10, 5, 13, 11, 10, 4, 8, 8, 9, 11, 1, 7},
	{5, 9, 6, 1, 8, 6, 2, 12, 11, 10, 4, 4, 7}}

func readLayout(scanner *bufio.Scanner) bool {
	for column := range 4 {
		if !scanner.Scan() {
			return false
		}
		line := strings.Split(scanner.Text(), " ")
		for index := range 13 {
			layout[column][index], _ = strconv.Atoi(line[index])
		}
	}
	return true
}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	scanner := bufio.NewScanner(os.Stdin)
	for readLayout(scanner) {
		createAHK(solve())
	}
}
