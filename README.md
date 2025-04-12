# What?
This is a mini-game similar to tic-tac-toe, but you should connect six pieces in a line instead of three to win. Also, unlike tic-tac-toe, it is possible to play with more than two players. The main notable feature of this implementation is the ability to develop an algorithm to play as a bot 😁 You can see a preview of the game in the picture below.

![Demo](https://github.com/alijarkani/connect/blob/master/images/demo.png?raw=true)

# Why?

Here's a funny story: Once upon a time, I hosted a friend who was highly skilled in Python. We were bored 😮‍💨 we had played all the board games we had, we had exhausted all topics of conversation. There wasn't anything to do; however, we were truly bored 😫 
I came up with an interesting idea: "How about building AI models that compete against each other?" I said, and he said, "Fascinating! 🤩 Let's do it".

The only question was which game would be appropriate for this? It was a little bit tricky 😵‍💫 The best game should've been a simple game that was implementable in a few hours, meanwhile, fun enough to amuse two bored programmers 🤔
We agreed on tic-tac-toe-style game, but the goal was connecting six pieces in a line instead of three. It was simple and fun enough, and it had a sufficiently large state space to challenge us 😃

Finally, we got started. After a few hours of hard work on implementing the game itself in the first step, then a few more hours to implement our own AI model, the time for battle has come 🤓
We ran the game ten times in different circumstances and let the AI models compete against each other. It was so exciting, much more than we expected! 🤩 I beat him up 6 to 4 😎 and taught him an important lesson: if somebody dares to compete against me, there will be consequences for him 😏 Just kidding, I was so lucky that day 😂

# How?
Running the game is so simple, first, you need to install dependencies:
```shell
pip install -r requirements.txt
```

Then, you need to configure the game. A basic configuration example exists in the repository with the name `main.py.dist`; you can simply use it or make your own configuration. Execute this command to use the default config.
```shell
cp main.py.dist main.py
```

Now you're good to go:
```shell
python main.py
```
