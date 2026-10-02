10 REM --- number guessing game ---
20 N = RND(100)
30 T = 0
40 PRINT "I picked a number from 1 to 100."
50 INPUT "Your guess? "; G
60 T = T + 1
70 IF G < N THEN PRINT "Too low!"
80 IF G > N THEN PRINT "Too high!"
90 IF G <> N THEN GOTO 50
100 PRINT "Correct in "; T; " tries!"
110 END
