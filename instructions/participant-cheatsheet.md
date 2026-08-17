# Operation Brewmaster — one page, keep it next to your laptop

## Getting going

1. Open **brewmaster** on GitHub at https://github.com/aaron-at-infoserv/brewmaster
2. Navigate to **Code** then **Codespaces** and create a codespace instance from the brewmaster project
3. It asks for secrets. **You can leave them blank** — the room shares one model endpoint and you don't need a key of your own.
4. In the terminal:

```bash
fcc-claude
```

If the agent stops answering, this fixes it — safe to run any time:

```bash
.devcontainer/start-agent.sh --restart
```

## What "working" looks like

The model thinks before it answers. Expect a pause, a burst of output, a tool call,
then another pause. **Roughly 25 seconds per step**, so a ten-step task runs four or
five minutes.

**That is not a hang.** Don't reach for `Esc` in the first thirty seconds because you'll interrupt it mid-thought and have to start again. Quiet for over a minute is a different matter.

## The seven-step loop — this is the whole session

```
1.  /clear                     fresh context between every task
2.  Plan mode (Shift+Tab)      let it explore before it edits
3.  Read the plan. Reject it if it's wrong.
4.  "Write a FAILING test for this ticket."
5.  Run it. Watch it fail. (If it passes, the TEST is wrong.)
6.  "Now make it pass. Don't change the test."
7.  git diff — read every line — then commit.
```

## Commands worth knowing today

| Command | Description |
| --- | --- |
| `/clear` | Wipe context. Use it far more than feels necessary. |
| `Shift+Tab` | Cycle permission mode — plan / normal / auto-accept |
| `/permissions` | Pre-approve safe things (`git status`, `pytest`) so it stops asking |
| `/review` | Our house review rules, committed in the repo |
| `Esc` | Interrupt — but read "What working looks like" above first |
| Switching model | **Not** `/model`. Run `MODEL=<provider>/<model> .devcontainer/start-agent.sh --restart` |

## Prompts that work

```
Explain how X works. Don't change anything.
```
```
Here's the command that fails and the last 40 lines of output.
Give me 5 ranked hypotheses and the cheapest test for each. No code yet.
```
```
Write a failing test that reproduces issue #12. Run it and show me it failing.
```
```
Hypothesis 2 was wrong — here's what I actually saw. Update your ranking.
```

## Prompts that don't

```
fix the bug                    ← no evidence, no oracle, no chance
make the tests pass            ← it will happily delete the test
refactor this                  ← refactor to what? by what measure?
was that wrong?                ← it will apologise enthusiastically and teach you nothing
```

## When it tells you something false — and it will

Two different problems, two different defences:

| | It **invented** it | It **inherited** it |
| --- | --- | --- |
| Sounds like | "There's no README in this repo" | "Money is held as integer pence" |
| Actually | Pattern-matched from other codebases | Read out of *our* docs, faithfully |
| Kill it with | `ls`, `grep`, a test — seconds | Nothing. Our docs lie. Fix the docs |

**The cheapest oracle in the room is `ls`.** Use it before you believe a claim about
what does or doesn't exist.

## The three habits that separate this from vibe coding

1. **Give it an oracle.** A failing test, a compiler error, a log. Without one it is
   guessing and so are you.
2. **Small context, small ask.** One file, one behaviour, one `/clear`. Long sessions
   rot.
3. **Read the diff.** Every line. If you can't explain it, don't commit it.

## Things it is genuinely good at

Exploring unfamiliar code · writing the boring test cases · generating hypotheses ·
turning rambling requirements into structured ones · spotting inconsistency in a diff ·
the tedious mechanical refactor you keep putting off

## Things it is genuinely bad at

Knowing whether it's right · knowing which files exist without looking · your business
rules · money and precision · anything where the failure is a hang rather than an
error · deciding whether the thing should be built at all

## Today's rules

- **Sandbox only.** Nothing from the real codebase goes near this.
- **You own what you commit.** "The AI wrote it" is not a defence.
- **Points off for any line you can't explain.** Random spot checks. Sorry.
