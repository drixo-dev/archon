####################################################

Development Workflow Rules

####################################################

21.

Implement one task at a time.

Never combine multiple features into one implementation.

Every implementation should be independently testable.

---------------------

22.

After implementing code, STOP.

Do not continue implementing the next feature automatically.

---------------------

23.

Always provide the exact commands the developer should run.

Examples

docker compose up -d --build

docker compose exec api bash

python -m scripts.test_repository_chat

curl ...

pytest ...

---------------------

24.

The developer executes all commands.

Never assume tests passed.

Wait for the developer to share the output before making further changes.

---------------------

25.

Every implementation must include a verification checklist.

Example

✓ Server starts

✓ Endpoint returns 200

✓ Response shape is correct

✓ Database updated

✓ No traceback

---------------------

26.

If verification fails,

debug only the current feature.

Never continue implementing new features until the current feature passes.

---------------------

27.

Never commit code.

Never push code.

The developer performs

git add

git commit

git push

only after successful verification.

---------------------

28.

Do not automatically modify unrelated files.

Only touch files required for the current task.

List all modified files before implementation.

---------------------

29.

Before implementation,

briefly explain

• What is being built

• Why it is needed

• Expected output

Maximum 10 lines.

Then implement.

---------------------

30.

After implementation,

provide

1. Modified files

2. Commands to run

3. Expected output

4. Common errors to check

5. Wait for results

Do not continue until results are provided.

---------------------

31.

Never execute terminal commands on behalf of the developer unless explicitly requested.

The terminal remains under the developer's control.

---------------------

32.

Never create Git commits or pull requests.

The developer owns the Git history.

---------------------

33.

When a feature passes verification,

explicitly state

"Feature Complete"

before moving to the next task.

---------------------

34.

If implementation requires new dependencies,

state them clearly before code changes.

Do not silently introduce libraries.

---------------------

35.

Update CURRENT_STATE.md only after the feature has been successfully verified by the developer.

Never update project status before successful verification.

---------------------

36.

Never redesign completed architecture during implementation.

Follow the approved documentation.

If an architectural issue is discovered,

stop,

explain it,

and request approval before changing the design.

####################################################

####################################################

Learning Mode Rules

####################################################

37.

Implementation takes priority over explanation.

Implement the requested task first.

Do not spend time teaching concepts unless explicitly requested.

---------------------

38.

After successful verification,

the developer may request a code review or architectural explanation.

At that point,

explain the implementation in depth using the project's Response Specification.

---------------------

39.

Never interrupt implementation with design discussions unless a blocking architectural issue exists.

---------------------

40.

Focus on delivering a working MVP first.

Optimization,

refactoring,

and deep educational explanations are postponed until after MVP completion.

####################################################    