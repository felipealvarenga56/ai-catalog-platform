"""Unit tests for the contract parser and serializer — tasks 2.1, 2.2."""

import pytest
from api.contract_parser import parse_contract, serialize_contract
from api.models import ContractCreate, ContractInitiative, ContractStatus


EXAMPLE_CONTRACT = """\
dataAI_Contract
id: 556706 (businessMap)
info:
  title: Recusa de oferta de vacina
  area: OPF
  initiative: Deep
  version: 1.0.0
  description: |
    Utilizar os registros de ofertas recusadas/aceitas (armazenados no MongoDB do AV) para implementar lógica de re-ofertas aos clientes, respeitando um período de stand-by de 7 dias após recusa.
Como sistema de ofertas,
Preciso rastrear e respeitar as recusas de clientes,
Para que não façamos re-ofertas indesejadas durante um período de 7 dias após recusa.

  owner: Data Science Enablement Team
  status: active
  contact:
    name: Jane Smith (ML Ops Engineer)
    email: jane.smith@rdsaude.com.br
  sec_approval: https://s3.rdsaude.com.br/approvals/approval.jpg
  docs_link: https://wiki-hyt.ds.dados.rd.com.br/e/pt-br/MLOps/contrato

terms:
  usage: |
    Conectado diretamente no TR, interação estrita atrás do balcão.
\tAo oferecer uma oferta personalizada gerada pelo time de IA, caso o cliente recuse a oferta, o atendente declara a recusa através de botão desenvolvido pelo time da Squad do TR e o sistema automaticamente define recusas com base em regras de negócio, para que a oferta não seja repetida em tempo pré determinado.
  limitations: nenhuma
"""


class TestParseExampleContract:
    """Test parsing the provided dataAI_Contract_ex1.txt example."""

    def test_parses_business_map_id(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.business_map_id == "556706"

    def test_parses_title(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.title == "Recusa de oferta de vacina"

    def test_parses_area(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.area == "OPF"

    def test_parses_initiative(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.initiative == ContractInitiative.DEEP

    def test_parses_version(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.version == "1.0.0"

    def test_parses_multiline_description(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert "Utilizar os registros" in result.description
        assert "Como sistema de ofertas," in result.description
        assert "7 dias após recusa." in result.description

    def test_parses_owner(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.owner == "Data Science Enablement Team"

    def test_parses_status(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.status == ContractStatus.ACTIVE

    def test_parses_contact_name(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.contact_name == "Jane Smith (ML Ops Engineer)"

    def test_parses_contact_email(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.contact_email == "jane.smith@rdsaude.com.br"

    def test_parses_sec_approval(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.sec_approval == "https://s3.rdsaude.com.br/approvals/approval.jpg"

    def test_parses_docs_link(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.docs_link == "https://wiki-hyt.ds.dados.rd.com.br/e/pt-br/MLOps/contrato"

    def test_parses_multiline_usage(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert "Conectado diretamente no TR" in result.usage
        assert "oferta personalizada" in result.usage

    def test_parses_limitations(self):
        result = parse_contract(EXAMPLE_CONTRACT)
        assert result.limitations == "nenhuma"


class TestParseContractErrors:
    """Test error handling for invalid inputs."""

    def test_missing_header_raises_valueerror(self):
        with pytest.raises(ValueError, match="Missing dataAI_Contract header"):
            parse_contract("id: 123 (businessMap)\ninfo:\n  title: Test")

    def test_empty_input_raises_valueerror(self):
        with pytest.raises(ValueError, match="Missing dataAI_Contract header"):
            parse_contract("")

    def test_missing_required_title_raises_valueerror(self):
        text = """\
dataAI_Contract
id: 100 (businessMap)
info:
  area: OPF
  initiative: Deep
  description: Some description
  owner: Team
"""
        with pytest.raises(ValueError, match="title"):
            parse_contract(text)

    def test_missing_required_initiative_raises_valueerror(self):
        text = """\
dataAI_Contract
id: 100 (businessMap)
info:
  title: Test
  area: OPF
  description: Some description
  owner: Team
"""
        with pytest.raises(ValueError, match="initiative"):
            parse_contract(text)

    def test_missing_id_raises_valueerror(self):
        text = """\
dataAI_Contract
info:
  title: Test
  area: OPF
  initiative: Deep
  description: Some description
  owner: Team
"""
        with pytest.raises(ValueError, match="id"):
            parse_contract(text)

    def test_missing_multiple_required_fields(self):
        text = """\
dataAI_Contract
id: 100 (businessMap)
info:
  owner: Team
"""
        with pytest.raises(ValueError, match="Missing required fields"):
            parse_contract(text)


class TestParseContractEdgeCases:
    """Test edge cases in parsing."""

    def test_minimal_valid_contract(self):
        text = """\
dataAI_Contract
id: 999 (businessMap)
info:
  title: Minimal
  area: IT
  initiative: BI
  description: A short description
  owner: Someone
"""
        result = parse_contract(text)
        assert result.business_map_id == "999"
        assert result.title == "Minimal"
        assert result.initiative == ContractInitiative.BI
        assert result.usage is None
        assert result.limitations is None
        assert result.contact_name is None

    def test_no_terms_section(self):
        text = """\
dataAI_Contract
id: 200 (businessMap)
info:
  title: No Terms
  area: Legal
  initiative: Copilot
  description: Testing without terms
  owner: Legal Team
"""
        result = parse_contract(text)
        assert result.usage is None
        assert result.limitations is None

    def test_leading_blank_lines(self):
        text = """\

dataAI_Contract
id: 300 (businessMap)
info:
  title: Blank Lines
  area: OPF
  initiative: Deep
  description: Has leading blanks
  owner: Team
"""
        result = parse_contract(text)
        assert result.business_map_id == "300"


class TestSerializeContract:
    """Test serialization of ContractCreate objects — task 2.2."""

    def _make_contract(self, **overrides) -> ContractCreate:
        defaults = dict(
            business_map_id="100",
            title="Test Contract",
            area="IT",
            initiative=ContractInitiative.DEEP,
            description="A simple description",
            owner="Team A",
        )
        defaults.update(overrides)
        return ContractCreate(**defaults)

    def test_serializes_header(self):
        text = serialize_contract(self._make_contract())
        assert text.startswith("dataAI_Contract\n")

    def test_serializes_id_line(self):
        text = serialize_contract(self._make_contract(business_map_id="556706"))
        assert "id: 556706 (businessMap)" in text

    def test_serializes_info_section(self):
        text = serialize_contract(self._make_contract())
        assert "\ninfo:\n" in text

    def test_serializes_title(self):
        text = serialize_contract(self._make_contract(title="My Title"))
        assert "  title: My Title\n" in text

    def test_serializes_initiative_enum_value(self):
        text = serialize_contract(self._make_contract(initiative=ContractInitiative.WIDE_N8N))
        assert "  initiative: wide-n8n\n" in text

    def test_serializes_status_enum_value(self):
        text = serialize_contract(self._make_contract(status=ContractStatus.DEVELOPMENT))
        assert "  status: development\n" in text

    def test_serializes_single_line_description_inline(self):
        text = serialize_contract(self._make_contract(description="Short desc"))
        assert "  description: Short desc\n" in text
        assert "  description: |" not in text

    def test_serializes_multiline_description_with_pipe(self):
        text = serialize_contract(self._make_contract(description="Line one\nLine two"))
        assert "  description: |\n" in text
        assert "    Line one\n" in text
        assert "    Line two\n" in text

    def test_serializes_contact_block(self):
        c = self._make_contract(contact_name="Jane", contact_email="jane@test.com")
        text = serialize_contract(c)
        assert "  contact:\n" in text
        assert "    name: Jane\n" in text
        assert "    email: jane@test.com\n" in text

    def test_omits_contact_when_none(self):
        c = self._make_contract(contact_name=None, contact_email=None)
        text = serialize_contract(c)
        assert "contact:" not in text

    def test_omits_optional_fields_when_none(self):
        c = self._make_contract()
        text = serialize_contract(c)
        assert "sec_approval" not in text
        assert "docs_link" not in text
        assert "terms:" not in text

    def test_includes_terms_section_when_usage_present(self):
        c = self._make_contract(usage="Internal use only")
        text = serialize_contract(c)
        assert "\nterms:\n" in text
        assert "  usage: Internal use only\n" in text

    def test_includes_terms_section_when_limitations_present(self):
        c = self._make_contract(limitations="None known")
        text = serialize_contract(c)
        assert "\nterms:\n" in text
        assert "  limitations: None known\n" in text

    def test_multiline_usage_with_pipe(self):
        c = self._make_contract(usage="Line A\nLine B")
        text = serialize_contract(c)
        assert "  usage: |\n" in text
        assert "    Line A\n" in text
        assert "    Line B\n" in text


class TestSerializeRoundTrip:
    """Test that serialize -> parse produces equivalent objects."""

    def _make_contract(self, **overrides) -> ContractCreate:
        defaults = dict(
            business_map_id="500",
            title="Round Trip",
            area="OPF",
            initiative=ContractInitiative.DEEP,
            description="Simple description",
            owner="DS Team",
        )
        defaults.update(overrides)
        return ContractCreate(**defaults)

    def test_minimal_round_trip(self):
        c = self._make_contract()
        text = serialize_contract(c)
        c2 = parse_contract(text)
        assert c == c2

    def test_full_round_trip(self):
        c = self._make_contract(
            status=ContractStatus.DEVELOPMENT,
            contact_name="Jane",
            contact_email="jane@test.com",
            sec_approval="https://sec.com",
            docs_link="https://docs.com",
            usage="Internal use",
            limitations="None",
        )
        text = serialize_contract(c)
        c2 = parse_contract(text)
        assert c == c2

    def test_multiline_round_trip(self):
        """Serialize -> parse -> serialize -> parse is stable (idempotent).

        The first serialize -> parse adds 4-space indentation to multi-line
        content. After that, subsequent cycles are stable.
        """
        c = self._make_contract(
            description="First line\nSecond line\nThird line",
            usage="Usage line 1\nUsage line 2",
        )
        text1 = serialize_contract(c)
        c2 = parse_contract(text1)
        # Second cycle should be stable
        text2 = serialize_contract(c2)
        c3 = parse_contract(text2)
        assert c2 == c3

    def test_parse_serialize_parse_round_trip(self):
        """Parse an existing text, serialize it, parse again — second cycle stable."""
        original = parse_contract(EXAMPLE_CONTRACT)
        text = serialize_contract(original)
        reparsed = parse_contract(text)
        # Do a second cycle to verify stability
        text2 = serialize_contract(reparsed)
        reparsed2 = parse_contract(text2)
        assert reparsed == reparsed2
