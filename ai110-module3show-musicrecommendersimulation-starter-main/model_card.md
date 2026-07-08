# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The main weakness I found is that my energy score never punishes a bad match, it only adds points. I use `1 - abs(song_energy - target)`, and since energy sits between 0 and 1, every song still walks away with some energy points. So even when nothing really fits the user, the system still hands back a confident top 5. My "sad + high energy" test proved this: "sad" isn't even a mood in my catalog and I gave no genre, so mood and genre could never match, yet the recommender still ranked five high energy songs like they were great picks. It also over-trusts genre, so a pop song with the wrong mood (Gym Hero, which is intense not happy) beats a happy song from another genre. And the catalog is only 18 songs, so a few genres barely show up and the variety is thin.

---

## 7. Evaluation  

I tested four profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and a
conflicting one (sad mood + high energy). Here's what each one printed.

**High-Energy Pop** `{genre: pop, mood: happy, energy: 0.9}`

```
1. Sunrise City by Neon Echo  (score 3.92)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.92)
2. Gym Hero by Max Pulse  (score 2.97)
   why: genre match (+2.0), energy close to target (+0.97)
3. Rooftop Lights by Indigo Parade  (score 1.86)
   why: mood match (+1.0), energy close to target (+0.86)
4. Storm Runner by Voltline  (score 0.99)
   why: energy close to target (+0.99)
5. Voltage Drop by Pulsewave  (score 0.95)
   why: energy close to target (+0.95)
```

**Chill Lofi** `{genre: lofi, mood: chill, energy: 0.3, likes_acoustic: True}`

```
1. Library Rain by Paper Lanterns  (score 4.45)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.95), acoustic pick (+0.5)
2. Midnight Coding by LoRoom  (score 4.38)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.88), acoustic pick (+0.5)
3. Focus Flow by LoRoom  (score 3.40)
   why: genre match (+2.0), energy close to target (+0.90), acoustic pick (+0.5)
4. Spacewalk Thoughts by Orbit Bloom  (score 2.48)
   why: mood match (+1.0), energy close to target (+0.98), acoustic pick (+0.5)
5. Moonlit Sonata Redux by Clara Vance  (score 1.50)
   why: energy close to target (+1.00), acoustic pick (+0.5)
```

**Deep Intense Rock** `{genre: rock, mood: intense, energy: 0.95}`

```
1. Storm Runner by Voltline  (score 3.96)
   why: genre match (+2.0), mood match (+1.0), energy close to target (+0.96)
2. Gym Hero by Max Pulse  (score 1.98)
   why: mood match (+1.0), energy close to target (+0.98)
3. Voltage Drop by Pulsewave  (score 1.00)
   why: energy close to target (+1.00)
4. Iron Verdict by Ashen Crown  (score 0.98)
   why: energy close to target (+0.98)
5. Sunrise City by Neon Echo  (score 0.87)
   why: energy close to target (+0.87)
```

**Conflicting (sad + high energy)** `{mood: sad, energy: 0.95}`

```
1. Voltage Drop by Pulsewave  (score 1.00)
   why: energy close to target (+1.00)
2. Gym Hero by Max Pulse  (score 0.98)
   why: energy close to target (+0.98)
3. Iron Verdict by Ashen Crown  (score 0.98)
   why: energy close to target (+0.98)
4. Storm Runner by Voltline  (score 0.96)
   why: energy close to target (+0.96)
5. Sunrise City by Neon Echo  (score 0.87)
   why: energy close to target (+0.87)
```

### What surprised me

Gym Hero kept popping up. For the Happy Pop user it lands at #2 even though the
song's mood is "intense," not happy. Here's the plain version: my system gives a
big +2 just for being pop, and Gym Hero is pop with high energy, so those points
alone push it past songs that actually match the "happy" feeling. It matches the
label the user asked for (pop) without matching the vibe (happy).

### Comparing the profiles

- **High-Energy Pop vs Chill Lofi:** total opposites, and the output shows it. Pop pulls bright, high energy pop tracks; lofi pulls calm, low energy, acoustic ones. The acoustic bonus only kicks in for the lofi user because they set `likes_acoustic: True`. This is the system working the way I want.
- **High-Energy Pop vs Deep Intense Rock:** both want high energy, so the bottom of both lists shares the same loud songs (Storm Runner, Voltage Drop). The tops differ because genre splits them: pop songs win for the pop user, rock wins for the rock user. Makes sense.
- **Chill Lofi vs Conflicting:** the cleanest match vs the messiest. Lofi hits genre, mood, energy, and acoustic all at once and scores over 4. The conflicting profile can't match genre or mood at all, so every song scores around 1 and it just ranks by energy. Same code, but one gets a real recommendation and the other basically gets a coin flip dressed up as a top 5.

### Experiment

I doubled energy's weight and halved genre's (genre 1.0, energy weight 2.0). For the Happy Pop user, off-genre high energy songs like Storm Runner (rock) and Voltage Drop (edm) climbed up the list because genre no longer carried them down. The results got more *different*, not more *accurate*, since I still want a pop fan to mostly hear pop. So I kept my original weights.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
