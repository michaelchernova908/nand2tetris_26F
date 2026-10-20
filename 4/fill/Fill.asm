// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// Fill.asm
// If a key is pressed, fill the screen black.
// If no key is pressed, clear the screen.

// Fill.asm
// If a key is pressed, fill the screen black.
// If no key is pressed, clear the screen.


// R0 will keep track of where we are currently writing on the screen.

@SCREEN             // A = 16384, the starting address of the screen
D=A                 // D = 16384
@R0                 // A = address of R0 (RAM[0])
M=D                 // RAM[0] = 16384
                    // R0 now points to the first screen word


// MAIN LOOP
(LOOP)
    // Check whether a key is currently being pressed

    @KBD             // A = 24576, the address of the keyboard
    D=M              // D = RAM[24576]
                     // D contains the current keyboard value
                     // D = 0 means no key is pressed
                     // D != 0 means a key is pressed

    // If a key is pressed, go to BLACK
    @BLACK            // A = address of BLACK
    D;JNE             // If D != 0, jump to BLACK

    // Otherwise, no key is pressed, so go to WHITE
    @WHITE            // A = address of WHITE
    0;JMP             // Unconditionally jump to WHITE


// BLACK
// Write black to the current screen word

(BLACK)

    // R0 contains the address of the screen word we want to modify.

    @R0               // A = address of R0 (RAM[0])
    A=M               // A = RAM[0] = value stored in R0
                      // A now contains the screen address
    M=-1              // RAM[A] = -1 (Black)


    // Move R0 to the next screen word

    @R0               // A = address of R0
    M=M+1             // R0 = R0 + 1

    // Have we reached the end of the screen?
    //
    // SCREEN = 16384
    // KBD    = 24576
    //
    @R0               // A = address of R0
    D=M               // D = current value of R0

    @KBD              // A = 24576
    D=D-A             // D = R0 - 24576
                      //
                      // If R0 < 24576:
                      //     D is negative
                      //
                      // If R0 = 24576:
                      //     D is zero
                      //
                      // If R0 > 24576:
                      //     D is positive


    // If R0 is still inside the screen, keep going

    @LOOP              // A = address of LOOP
    D;JLT              // If D < 0, jump back to LOOP


    // If we get here, That means we reached the end of the screen.
    // Start again at the beginning of the screen.

    // Otherwise, stay at the end
    // Reset R0 to the address immediately after the screen
    @KBD
    D=A
    @R0
    M=D                            

    @LOOP
    0;JMP              // Unconditionally jump back to main loop


// WHITE
// Erase the most recently written black screen word


(WHITE)

    // R0 currently points to the NEXT screen word.
    //
    // So we first move R0 backward by one.


    @R0               // A = address of R0
    M=M-1              // R0 = R0 - 1
                      // R0 now points to the most recently
                      // written screen word

    @R0               // A = address of R0
    A=M               // A = value stored in R0
                      // A now contains the screen address

    M=0               // RAM[A] = 0
                      // Clear the screen word


    // Make sure R0 hasn't gone before the beginning of
    // the screen.
    //
    // SCREEN starts at address 16384.


    @R0               // A = address of R0
    D=M               // D = current value of R0

    @SCREEN           // A = 16384
    D=D-A             // D = R0 - 16384
                      //
                      // If R0 >= 16384:
                      //     D >= 0
                      //
                      // If R0 < 16384:
                      //     D < 0


    // If R0 is still on the screen, go check the keyboard

    @LOOP               // A = address of LOOP
    D;JGE               // If D >= 0, jump to LOOP


    // If we get here, R0 went before the beginning of the screen.
    // Reset R0 back to SCREEN.


    @SCREEN             // A = 16384
    D=A                 // D = 16384

    @R0                 // A = address of R0
    M=D                 // R0 = 16384


    @LOOP               // A = address of LOOP
    0;JMP               // Go back to checking the keyboard








