from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
WORKFLOW_ROOT = REPOSITORY_ROOT / ".github" / "workflows"


def load_workflow(name: str) -> dict[str, object]:
    return yaml.load(
        (WORKFLOW_ROOT / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )


def trigger_paths(workflow: dict[str, object], event: str) -> list[str]:
    events = workflow["on"]
    assert isinstance(events, dict)
    config = events[event]
    assert isinstance(config, dict)
    paths = config["paths"]
    assert isinstance(paths, list)
    return [str(path) for path in paths]


def test_app_and_corpus_triggers_are_separate_with_dual_check_paths() -> None:
    app = load_workflow("app-ci.yml")
    corpus = load_workflow("corpus-ci.yml")
    for event in ("pull_request", "push"):
        app_paths = trigger_paths(app, event)
        corpus_paths = trigger_paths(corpus, event)

        assert "apps/scut-senior/knowledge/**" not in app_paths
        assert "apps/scut-senior/knowledge/**" in corpus_paths
        assert "apps/scut-senior/worker/**" in corpus_paths
        assert "apps/scut-senior/packages/**" in corpus_paths
        assert "apps/scut-senior/**" in app_paths
        assert "apps/scut-senior/web/**" not in corpus_paths
        assert "apps/scut-senior/api/**" not in corpus_paths


def test_corpus_ci_builds_a_fixed_real_candidate_without_activation() -> None:
    text = (WORKFLOW_ROOT / "corpus-ci.yml").read_text(encoding="utf-8")

    assert "--manifest apps/scut-senior/knowledge/manifest.csv" in text
    assert "--knowledge-root apps/scut-senior/knowledge" in text
    assert "/apps/scut-senior/knowledge/" in text
    assert 'PYTHONDONTWRITEBYTECODE: "1"' in text
    assert "python -m scut_senior_worker.corpus_builder build" in text
    assert 'source_commit="$(git rev-parse HEAD)"' in text
    assert '--source-commit "${source_commit}"' in text
    assert "--repository-root ." in text
    assert "python -m scut_senior_worker.corpus_builder validate" in text
    assert "git ls-files -- 'active.json' ':(glob)**/active.json'" in text
    assert 'find "${store_root}" -type f -name active.json' in text
    assert "scut_senior_worker.corpus_builder activate" not in text
    assert "apps/scut-senior/tests/python/test_corpus_builder.py" in text
    assert "apps/scut-senior/tests/fixtures/corpus/manifest.csv" in text


def test_ci_combines_partial_clone_sparse_checkout_and_lfs_skip() -> None:
    for name in ("app-ci.yml", "corpus-ci.yml"):
        text = (WORKFLOW_ROOT / name).read_text(encoding="utf-8")
        assert 'GIT_LFS_SKIP_SMUDGE: "1"' in text
        assert "--filter=blob:none" in text
        assert "git sparse-checkout set" in text
        assert 'test ! -e "学科资料"' in text


def test_deployment_is_protected_and_never_runs_for_pull_requests() -> None:
    workflow = load_workflow("app-deploy.yml")
    events = workflow["on"]
    assert isinstance(events, dict)
    assert "pull_request" not in events
    jobs = workflow["jobs"]
    assert isinstance(jobs, dict)
    validation_job = jobs["validation-only"]
    assert isinstance(validation_job, dict)
    assert "environment" not in validation_job
    text = (WORKFLOW_ROOT / "app-deploy.yml").read_text(encoding="utf-8")
    assert "vars.DEPLOYMENT_ENABLED == 'true'" in text
    assert "github.repository == 'AlexBybye/SCUT_CS'" in text
    assert "scut-senior-production" in text
    assert "validation_only" in text
    assert "Validate the bounded deployment skeleton" in text
    assert "without logging in to SWR" in text
    assert "secrets." not in text
    assert "exit 1" in text


def test_docker_build_context_is_bounded_to_application_directory() -> None:
    app_ci = (WORKFLOW_ROOT / "app-ci.yml").read_text(encoding="utf-8")
    deploy = (WORKFLOW_ROOT / "app-deploy.yml").read_text(encoding="utf-8")

    expected = "--file apps/scut-senior/Dockerfile"
    assert expected in app_ci
    assert expected in deploy
    assert "apps/scut-senior\n" in app_ci
    assert "apps/scut-senior\n" in deploy

    # knowledge 已移入 apps/scut-senior/knowledge：镜像边界改由 .dockerignore
    # 保证，两个工作流都必须显式断言该排除规则存在。
    for text in (app_ci, deploy):
        assert "grep -qx 'knowledge' apps/scut-senior/.dockerignore" in text
    dockerignore = (
        REPOSITORY_ROOT / "apps/scut-senior" / ".dockerignore"
    ).read_text(encoding="utf-8")
    assert "\nknowledge\n" in dockerignore
