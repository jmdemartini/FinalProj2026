# Status Report

#### Your name

James De Martini

#### Your section leader's name

Daniel Blitshtein

#### Project title

Mario Superstar Baseball Stat Accumulator

***

Short answers for the below questions suffice. If you want to alter your plan for your project (and obtain approval for the same), be sure to email your section leader directly!

#### What have you done for your project so far?

I'm basically done, I have the script that creates the csv and reads and accumulates from the stat files, I am just working on getting more advanced stats in the sheet. I have stuff like avg, hits, slg, ops, obp, outs responsible for, K/9, ERA, and top ten counting and rate leaders for each stat.

#### What have you not done for your project yet?

I am struggling pulling "Games Played" because I have to calculate it from total outs in the field for each character and I'm having trouble finding how to pull it efficiently without having to read every single event that took place.

#### What problems, if any, have you encountered?

Defensive efficiency and error% have been really difficult, as the game records them by scowering every single event that took place and sees if it had a character make an error, and has a different statement for every character that touches the ball in the event. With 27 outs and averaging nearly 12 hitters a game, that's nearly 40 events per game. I could accomplish this with a for loop or something, I'm just struggling to make it work.
