// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.

// R2 will hold our running result.
// Since we haven't added anything yet, start the result at 0.

@R2                 // A = address of R2 (RAM[2])
M=0                 // RAM[2] = 0
                    // R2 now contains 0



// INITIALIZE THE COUNTER

// We want to multiply:
//     R0 × R1
//
// We will do this by repeatedly adding R0 to itself.
//
// For example, if:
//     R0 = 5
//     R1 = 3
//
// We want:
//     5 + 5 + 5 = 15
//
// R3 will keep track of how many additions are still needed.

@R1                 // A = address of R1 (RAM[1])
D=M                 // D = RAM[1]
                    // D now contains the value of R1

@R3                 // A = address of R3 (RAM[3])
M=D                 // RAM[3] = D
                    // R3 now contains a copy of R1


// MULTIPLICATION LOOP

(LOOP)

    // Check whether our counter has reached 0.
    //
    // If R3 = 0, we have performed all the necessary
    // additions and multiplication is complete.

    @R3                 // A = address of R3
    D=M                 // D = RAM[3]
                        // D now contains the current counter


    // If D = 0, jump to END.

    @END                // A = address of END
    D;JEQ               // If D == 0, jump to END
                        // JEQ = Jump if Equal to Zero

    // ADD R0 TO THE RUNNING RESULT
    

    // First, load the value of R0 into D.

    @R0                 // A = address of R0 (RAM[0])
    D=M                 // D = RAM[0]
                        // D now contains the value of R0


    // Now add R0 to the current value of R2.
    //
    // We want:
    //
    //     R2 = R2 + R0
    //
    // Since D currently contains R0, we can use:
    //
    //     M = D + M
    //
    // where M refers to the current RAM location,
    // which will be R2 after @R2.

    @R2                 // A = address of R2 (RAM[2])
    M=D+M               // R2 = R0 + R2

 
    // DECREASE THE COUNTER

    @R3                 // A = address of R3
    M=M-1               // R3 = R3 - 1

    // REPEAT THE LOOP

    // Go back to the beginning of the loop so we can:
    // 1. Check whether R3 has reached 0
    // 2. Add R0 to R2 again if necessary

    @LOOP               // A = address of LOOP
    0;JMP               // Unconditionally jump to LOOP


// ---------------------------------------------------------
// END OF MULTIPLICATION
// ---------------------------------------------------------

(END)

    // If we reach this point, R3 = 0.
    // Stay here forever.

    @END                
    0;JMP               



