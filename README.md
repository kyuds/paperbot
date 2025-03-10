# paperbot
Using LLM agents for paper suggestions

### Running
Please look at `sample-run-1.txt` and `sample-run-2.txt` to see the bot in operation. `sample-run-2.txt` is the same bot that ran the second time after the feedback was given that biology-related papers are to be excluded.
```
just run
```
** I have a private bot running in AWS that already scrapes and summarizes arXiv papers. This project aims to use these summaries to create personalized suggestions for papers. 

### TODO
- [ ] Feedback in form of numeric scores, not descriptions. Providing descriptions is too much work for the user.
- [X] Ability to fluently control the number of papers returned (currently fixed to 5).
- [ ] Create Terraform system for cloud deployment.
