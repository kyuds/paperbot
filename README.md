# paperbot
Using LLM agents for paper suggestions

### Running
Please look at `sample-run.txt` to see the bot in operation.
```
just run
```
** I have a private bot running in AWS that already scrapes and summarizes arXiv papers. This project aims to use these summaries to create personalized suggestions for papers. 

### TODO
- [ ] Feedback in form of numeric scores, not descriptions. Providing descriptions is too much work for the user.
- [ ] Ability to fluently control the number of papers returned (currently fixed to 5).
- [ ] Create Terraform system for cloud deployment.
