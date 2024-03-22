type ArrayOf4<T> = [T, T, T, T];

type Card = number;
type Score = number;
type Stack = Card[];
type Layout = ArrayOf4<Stack>;
// type State = {cardsLeft: ArrayOf4<number>, score: number};
// type Solution = {stack: Stack, stackValue: number, score: number, card};
// enum Action {
//     Grab0 = 0,
//     Grab1 = 1,
//     Grab2 = 2,
//     Grab3 = 3,
// };

type Action = 0|1|2|3;
const ACTIONS: ArrayOf4<Action> = [0,1,2,3];

type StateHash = number;
// type Step = {score: number, parent: Step, actions: Action[]}

const JACK = 11;

const best: Map<StateHash, State> = new Map();

class State {
    public hash: StateHash;
    constructor(
        public layout:Layout, 
        public cardsLeft: ArrayOf4<number>, 
        public score:Score, 
        public parent: State|null, 
        public actions: Action[], 
        private bonuses: string[]
    ) {
        this.hash = cardsLeft[0]+(cardsLeft[1]+(cardsLeft[2]+cardsLeft[3]*14)*14)*14;
    }

    public * possibleStates():Generator<State> {
        yield * this.internalPossibleStates([], this.score, 0, [], this.cardsLeft, []);
    }

    private * internalPossibleStates(stack: Stack, score: Score, stackValue: number, actions: Action[], playingCardsLeft: ArrayOf4<number>, bonuses: string[]):Generator<State> {
        let endStack = true;
        for (const action of ACTIONS) {
            if (playingCardsLeft[action] > 0) {
                const card = this.layout[action][playingCardsLeft[action]-1];
                const cardValue = card > 10 ? 10 : card;
                const newStackValue = stackValue + cardValue;
                if (newStackValue <= 31) {
                    endStack = false;             
                    const newStack = [...stack, card];                    
                    const newActions = [...actions, action];
                    const newPlayingCardsLeft = [...playingCardsLeft] as ArrayOf4<number>;
                    newPlayingCardsLeft[action]--;

                    // Calc new score
                    let newScore = score;
                    let newBonuses = [...bonuses];
                    if (newStackValue === 15 || newStackValue === 31) {
                        newScore += 2;
                        if (newStackValue === 15) {
                            newBonuses.push('Sum of 15');
                        } else {
                            newBonuses.push('Sum of 31');
                        }                        
                    }

                    const lastCardIndex = stack.length-1;
                    if (card == stack[lastCardIndex]) {
                        if (card == stack[lastCardIndex-1]) {
                            if (card == stack[lastCardIndex-2]) {
                                newScore += 12;
                                newBonuses.push(`Four of ${card}`);
                            } else {
                                newScore += 6;
                                newBonuses.push(`Three of ${card}`);
                            }
                        } else {
                            newScore += 2
                            newBonuses.push(`Pair of ${card}`);
                        }
                    }

                    if (lastCardIndex < 0 && card == JACK) {
                        newScore += 2;
                        newBonuses.push(`Start with Jack`);
                    }

                    for (let straight = 7; straight >= 3; straight--) {
                        if (newStack.length >= straight) {
                            const range = newStack.slice(-straight);
                            const set = new Set(range);
                            if (set.size === straight) {
                                const min = Math.min(...range);
                                const max = Math.max(...range);
                                if (max-min === straight-1) {
                                    newScore += straight;
                                    newBonuses.push(`Straign of ${straight} from ${min} to ${max}`);
                                    break;
                                }
                            }
                        }
                    }
                    
                    yield * this.internalPossibleStates(newStack, newScore, newStackValue, newActions, newPlayingCardsLeft, newBonuses);
                    
                }
            }
        }
        if (endStack) {
            if (actions.length > 0) {
                yield new State(this.layout, playingCardsLeft, score, this, actions, bonuses);
            }
        }
    }

    public output() {
        console.log(`Score: ${this.score} Actions: ${this.actions.map(x=>x+1)}`);
        for (const bonus of this.bonuses) {
            console.log(` - ${bonus}`);
        }
        this.parent?.output();
    }
}

// const layout:Layout = [
//     [1,2,3,4,5,6,7,8,9,10,11,12,13],
//     [1,2,3,4,5,6,7,8,9,10,11,12,13],
//     [1,2,3,4,5,6,7,8,9,10,11,12,13],
//     [1,2,3,4,5,6,7,8,9,10,11,12,13]
// ];

// const layout:Layout = [
//     [ 6, 3, 9,12,11, 6, 8,11, 5, 3, 7, 3, 1],
//     [13,11, 4,13, 7, 1,12,12, 2, 9, 9, 6,13],
//     [ 4,13,10, 8, 6, 1, 8, 5, 4,10, 2, 8, 7],
//     [11,10, 5, 5, 9, 1,12, 2, 7, 2, 4,10, 3],
// ];

// const layout:Layout = [
//     [13, 1,10, 7,13, 4,11, 5, 2,13,12, 6, 4],
//     [10, 7, 1, 2, 6, 5,11, 4, 7, 1, 4, 2,10],
//     [12, 9, 8, 8, 2, 8, 1,11,13, 9, 3, 6, 6],
//     [12,12, 5, 3, 9,10, 9, 5, 3, 7, 3, 8,11],
// ];

// 3, 2, 4, 5, 1, 6, 7, 3,


// 110 score!

// const layout:Layout = [[10,  9,  8,  2,  2,  7,  5,  1,  7,  4, 13,  2, 11],
//         [ 6,  6,  1,  7,  4,  2,  9, 11, 12, 10,  8,  8, 10],
//         [ 8,  3, 10,  6,  3, 13,  5, 12,  9,  5,  3, 13, 12],
//         [ 7, 12,  1,  9,  6,  1,  4,  3,  4, 11, 11,  5, 13]];


// const layout:Layout = [[ 1,  2,  6,  6,  4,  7,  3, 10, 13,  3,  5,  5,  9],
//  [ 9,  2, 11, 12,  8,  7,  2, 13,  9,  1, 11,  6,  1],
//  [ 9, 13, 12,  2,  7, 13,  8, 10,  6,  4, 10, 12, 11],
//  [ 1, 12,  8,  3, 10,  3,  5,  8,  4, 11,  7,  5,  4]]



const layout:Layout = [[10,  6,  8,  6,  3,  7,  5, 10, 10, 11, 12,  1, 13],
                       [13,  3,  1,  8,  3,  4,  5,  6,  3, 12,  1,  2,  9],
                       [ 2, 11,  5, 13,  1, 12,  7,  8,  7,  2,  5,  7,  9],
                       [11, 11,  2,  4,  9,  4, 12, 13,  8,  9, 10,  4,  6]];

const INITIAL_STATE = new State(layout, [13,13,13,13], 0, null, [], []);

let states = new Set<State>([INITIAL_STATE]);

while (states.size > 0) {
    const nextStates = new Set<State>();

    const total = states.size;
    let processed = 0;
    let childrenCount = 0;
    let replaced = 0
    let added = 0;
    let discarded = 0;

    for (const state of states) {
        for (const nextState of state.possibleStates()) {
            childrenCount ++;
            const previousBestState = best.get(nextState.hash);
            if (previousBestState === undefined || previousBestState.score < nextState.score) {
                if (previousBestState !== undefined) {
                    replaced ++;
                    nextStates.delete(previousBestState);
                } else {
                    added ++;
                }
                best.set(nextState.hash, nextState);
                nextStates.add(nextState);
            } else {
                discarded ++;
            }
        }
        processed++;
        // if (processed % 100 === 0) {
        //     console.log(`Processed ${processed}/${total}`);
        // }
    }
    console.log(`Total new states: ${childrenCount}`);
    console.log(`Average children: ${childrenCount/total}`);
    console.log(`Discarded: ${discarded}`);
    console.log(`New added: ${added}`);
    console.log(`Replaced: ${replaced}`);

    states = nextStates;
    // console.log(states.size)
}

// for (const x of best) {
//     console.log(x);
// }

best.get(0)?.output();