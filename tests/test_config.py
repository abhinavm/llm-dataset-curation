from pathlib import Path

from curation.config import PipelineConfig, load_config


def test_missing_file_returns_defaults(tmp_path: Path):
    config = load_config(tmp_path / "does_not_exist.yaml")
    assert config == PipelineConfig()


def test_loads_overrides_from_yaml(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
filter:
  min_words: 10
dedup:
  near_dedup_threshold: 0.9
tokenize:
  max_tokens_per_chunk: 512
ingest:
  language: fr
"""
    )
    config = load_config(config_path)
    assert config.filter.min_words == 10
    assert config.filter.max_words == PipelineConfig().filter.max_words  # unset keys keep defaults
    assert config.near_dedup_threshold == 0.9
    assert config.max_tokens_per_chunk == 512
    assert config.language == "fr"


def test_repo_config_yaml_loads_without_error():
    config = load_config()
    assert isinstance(config, PipelineConfig)
