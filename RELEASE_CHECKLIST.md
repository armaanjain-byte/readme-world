# README-World Release Checklist

Follow this checklist when initializing the repository or setting it up from a fresh fork.

## [ ] 1. Fork Setup
- Click the **Fork** button on the main repository.
- Ensure you have cloned the `main` branch.

## [ ] 2. Actions Permissions
- Navigate to your repository's **Settings > Actions > General**.
- Under **Workflow permissions**, ensure **Read and write permissions** are granted to GitHub Actions. This allows the engine to push `state.json` updates automatically.
- Check the box to "Allow GitHub Actions to create and approve pull requests" if you plan to accept community WorldPacks.

## [ ] 3. Output Branch Creation
- You don't need to do anything manually! The `update.yml` and `process_comment.yml` workflows are designed to intelligently detect if the `output` branch is missing and create an orphan branch automatically on their first run.

## [ ] 4. WorldPack Configuration
- Validate your active WorldPack locally by running `python validate_worldpack.py worldpacks/default` (or your custom directory).
- Edit `world.config.yml` (or run `python setup.py` locally) to specify your chosen WorldPack and Display Name.
- Push your changes to the `main` branch.

## [ ] 5. Issue Creation
- Go to the **Issues** tab.
- Create an issue titled exactly **Interact**.
- This issue serves as the "Controller" for all user commands. 
- *Note: Do not lock the issue. It must remain open for comments.*

## [ ] 6. First Interaction Test
- Go to your newly created issue.
- Comment `/pet`.
- Navigate to the **Actions** tab to watch the `Process Interaction Comment` workflow run.
- Once it completes, check your `README.md` to see your pet's mood change and the latest interaction log update!
