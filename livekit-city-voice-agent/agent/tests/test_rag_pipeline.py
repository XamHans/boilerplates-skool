"""
Comprehensive test suite for the Lüneburg VoiceBot RAG Pipeline.

Tests cover opening hours, service info, cross-domain queries, and edge cases.
"""

from contextlib import asynccontextmanager

import pytest
from livekit.agents import AgentSession, llm
from livekit.plugins import openai

from agent import Assistant


def _llm() -> llm.LLM:
    """Create LLM instance for testing."""
    return openai.LLM(model="gpt-4o-mini")


@asynccontextmanager
async def session_and_llm():
    async with (_llm() as llm_client, AgentSession(llm=llm_client) as session):
        await session.start(Assistant())
        yield llm_client, session


def expect_tool_pipeline(result):
    """Skip function call events (FunctionCallEvent, acknowledgment, and FunctionCallOutputEvent)."""
    result.expect.next_event()  # FunctionCallEvent
    result.expect.next_event()  # ChatMessageEvent (acknowledgment like "Einen Moment...")
    result.expect.next_event()  # FunctionCallOutputEvent


async def assert_intent(result, llm_client, intent: str, uses_tool: bool = True):
    """Assert that the assistant's response matches the given intent."""
    if uses_tool:
        expect_tool_pipeline(result)
    await (
        result.expect.next_event()  # ChatMessageEvent
        .is_message(role="assistant")
        .judge(llm_client, intent=intent)
    )


# ==============================================================================
# CATEGORY 1: OPENING HOURS QUERIES (10 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_direct_department_query() -> None:
    """Test direct department name query for opening hours."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wann hat das Einwohnermeldeamt geöffnet?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides opening hours for Einwohnermeldeamt, including weekday hours",
        )


@pytest.mark.asyncio
async def test_specific_day_query() -> None:
    """Test query for a specific day of the week."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Ist das Standesamt am Mittwoch offen?")
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that Standesamt (Registry Office) is closed on Wednesday",
        )


@pytest.mark.asyncio
async def test_multiple_departments() -> None:
    """Test query for multiple departments at once."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was sind die Öffnungszeiten für das Standesamt und das Sozialamt?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides opening hours for both Standesamt (Registry Office) and Sozialamt (Social Welfare Office)",
        )


@pytest.mark.asyncio
async def test_natural_language_variant() -> None:
    """Test natural language query that maps service to department."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich möchte mein Fahrzeug anmelden, wann kann ich kommen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides opening hours for Kfz-Zulassungsstelle (vehicle registration office)",
        )


@pytest.mark.asyncio
async def test_weekend_query() -> None:
    """Test query about weekend availability."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Kann ich das Standesamt am Samstag besuchen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that Standesamt (Registry Office) is available on Saturday by appointment (nach Vereinbarung)",
        )


@pytest.mark.asyncio
async def test_evening_availability() -> None:
    """Test query about evening hours."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Welche Ämter sind nach 17 Uhr geöffnet?")
        await assert_intent(
            result,
            llm_client,
            intent="Identifies offices that are open after 17:00, such as Einwohnermeldeamt on Thursday (until 18:00) or Kfz-Zulassungsstelle on Thursday (until 17:00)",
        )


@pytest.mark.asyncio
async def test_library_hours() -> None:
    """Test query for department not in our data - should say don't know."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wann hat die Stadtbibliothek geöffnet?")
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that information about Stadtbibliothek (City Library) opening hours is not available or not found",
        )


@pytest.mark.asyncio
async def test_vehicle_registration_hours() -> None:
    """Test query for vehicle registration office hours."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Öffnungszeiten der Kfz-Zulassungsstelle?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides opening hours for Kfz-Zulassungsstelle (Vehicle Registration Office)",
        )


@pytest.mark.asyncio
async def test_english_variant() -> None:
    """Test English language query - should still attempt to help."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="When is the Standesamt open?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides opening hours for Standesamt (Registry Office), responding to English query",
        )


@pytest.mark.asyncio
async def test_tomorrow_query() -> None:
    """Test query about tomorrow's hours."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Ist das Sozialamt morgen offen?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides information about Sozialamt (Social Welfare Office) hours for the next day",
        )


# ==============================================================================
# CATEGORY 2: SERVICE INFORMATION QUERIES (20 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_business_registration_procedure() -> None:
    """Test query about business registration procedure."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie melde ich ein Gewerbe in Lüneburg an?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains the procedure for registering a business (Gewerbe anmelden) in Lüneburg",
        )


@pytest.mark.asyncio
async def test_business_registration_documents() -> None:
    """Test query about required documents for business registration."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Welche Dokumente brauche ich für die Gewerbeanmeldung?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Lists required documents for business registration, such as ID/passport and possibly trade certificates",
        )


@pytest.mark.asyncio
async def test_business_registration_fees() -> None:
    """Test query about business registration fees."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Was kostet eine Gewerbeanmeldung?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides fee information for business registration",
        )


@pytest.mark.asyncio
async def test_business_registration_deadline() -> None:
    """Test query about business registration deadline."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wann muss ich mein Gewerbe anmelden?")
        await assert_intent(
            result,
            llm_client,
            intent="Explains that business must be registered immediately at the start of business activity",
        )


@pytest.mark.asyncio
async def test_address_change_process() -> None:
    """Test query about address change process."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin in eine neue Wohnung gezogen, was muss ich tun?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains the process for address change (Ummeldung), mentioning the 2-week deadline",
        )


@pytest.mark.asyncio
async def test_address_change_documents() -> None:
    """Test query about documents needed for address change."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was muss ich mitbringen, um meine Adresse zu ändern?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Mentions required documents for address change, including Wohnungsgeberbestätigung (landlord confirmation)",
        )


@pytest.mark.asyncio
async def test_id_card_address_update() -> None:
    """Test query about updating ID card after moving."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Muss ich meinen Personalausweis nach dem Umzug aktualisieren?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Confirms that ID card (Personalausweis) address must be updated after moving",
        )


@pytest.mark.asyncio
async def test_dog_deregistration() -> None:
    """Test query about dog deregistration process."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Mein Hund ist gestorben, wie melde ich ihn ab?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains how to deregister a dog, mentioning notification within 1 week and returning the tax tag",
        )


@pytest.mark.asyncio
async def test_dog_deregistration_fee() -> None:
    """Test query about dog deregistration fees."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Kostet die Hundeabmeldung eine Gebühr?")
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that there are no fees for dog deregistration",
        )


@pytest.mark.asyncio
async def test_death_certificate_eligibility() -> None:
    """Test query about who can request death certificates."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wer kann eine Sterbeurkunde beantragen?")
        await assert_intent(
            result,
            llm_client,
            intent="Explains who is eligible to request a death certificate, such as spouse, descendants, or siblings with legitimate interest",
        )


@pytest.mark.asyncio
async def test_death_certificate_cost() -> None:
    """Test query about death certificate fees."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Was kostet eine Sterbeurkunde?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides cost information for death certificates (e.g., 15 EUR for first copy, 7.50 EUR for additional)",
        )


@pytest.mark.asyncio
async def test_immigration_office_contact() -> None:
    """Test query about immigration office contact information."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie kann ich die Ausländerbehörde kontaktieren?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides contact details for Ausländerbehörde (Immigration Office), such as phone, email, or address",
        )


@pytest.mark.asyncio
async def test_elections_vote_by_mail() -> None:
    """Test query about voting by mail."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Kann ich in Lüneburg per Briefwahl abstimmen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Confirms that voting by mail (Briefwahl) is possible and mentions requesting a Wahlschein",
        )



@pytest.mark.asyncio
async def test_phone_contact_hours() -> None:
    """Test query about phone hours for a department."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wann kann ich das Einwohnermeldeamt telefonisch erreichen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides phone contact hours for Einwohnermeldeamt",
        )


@pytest.mark.asyncio
async def test_late_registration_penalty() -> None:
    """Test query about penalty for late registration."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was passiert, wenn ich mich zu spät nach dem Umzug anmelde?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Warns about possible fines (Bußgeld) for late registration after moving",
        )


@pytest.mark.asyncio
async def test_business_registration_processing_time() -> None:
    """Test query about business registration processing time."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wie lange dauert die Gewerbeanmeldung?")
        await assert_intent(
            result,
            llm_client,
            intent="Provides processing time for business registration (immediate if in person, or processing duration if by mail)",
        )


# ==============================================================================
# CATEGORY 3: CROSS-DOMAIN QUERIES (10 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_service_plus_hours_combined() -> None:
    """Test combined query about service and opening hours."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich muss ein Gewerbe anmelden, wann kann ich kommen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides both business registration information and Gewerbeamt opening hours",
        )


@pytest.mark.asyncio
async def test_document_plus_location() -> None:
    """Test query about document and location combined."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wo bekomme ich eine Geburtsurkunde und was sind die Öffnungszeiten?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides information about Standesamt (Registry Office) location/contact and opening hours for getting birth certificates",
        )


@pytest.mark.asyncio
async def test_multi_step_scenario() -> None:
    """Test multi-step scenario for new residents."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin gerade von Berlin nach Lüneburg gezogen. Was muss ich tun?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Outlines steps for new residents, including address registration (Anmeldung), ID update, and possibly other administrative tasks",
        )


@pytest.mark.asyncio
async def test_service_location_and_department() -> None:
    """Test query about service location and responsible department."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wo melde ich meine neue Adresse an?")
        await assert_intent(
            result,
            llm_client,
            intent="Identifies Einwohnermeldeamt/Bürgerbüro as the location for address registration and provides contact details",
        )


@pytest.mark.asyncio
async def test_fee_and_payment_method() -> None:
    """Test query about fees and payment methods."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was kostet ein Reisepass und wie kann ich bezahlen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides passport fee information and explains payment methods",
        )


@pytest.mark.asyncio
async def test_prerequisites_and_timeline() -> None:
    """Test query about prerequisites and processing timeline."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was brauche ich für eine Aufenthaltserlaubnis und wie lange dauert es?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Lists requirements for residence permit (Aufenthaltserlaubnis) and provides processing time information",
        )


@pytest.mark.asyncio
async def test_foreign_resident_newcomer() -> None:
    """Test scenario for foreign residents moving to Lüneburg."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich ziehe aus dem Ausland nach Lüneburg. Welche Ämter muss ich besuchen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Recommends visiting Einwohnermeldeamt (registration) and Ausländerbehörde (immigration office) for foreign residents",
        )


@pytest.mark.asyncio
async def test_business_owner_scenario() -> None:
    """Test scenario for starting a restaurant business."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich eröffne ein Restaurant. Welche Genehmigungen brauche ich?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Mentions business registration (Gewerbe) and possibly restaurant license (Gaststättenerlaubnis) requirements",
        )


@pytest.mark.asyncio
async def test_pet_owner_scenario() -> None:
    """Test scenario for new dog owners."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich habe einen neuen Hund bekommen. Was muss ich tun?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains dog registration requirements and dog tax (Hundesteuer) information",
        )


@pytest.mark.asyncio
async def test_document_replacement() -> None:
    """Test scenario for lost ID card replacement."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich habe meinen Personalausweis verloren. Wie bekomme ich einen neuen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains the process for replacing a lost ID card, including reporting the loss, applying for a new one, and fee information",
        )


# ==============================================================================
# CATEGORY 4: EDGE CASES & ERROR HANDLING (10 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_out_of_scope_weather() -> None:
    """Test handling of out-of-scope query about weather."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wie ist das Wetter in Lüneburg heute?")
        await assert_intent(
            result,
            llm_client,
            intent="Politely declines to answer weather questions, staying focused on city administration services",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_ambiguous_query() -> None:
    """Test handling of ambiguous registration query."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wie melde ich etwas an?")
        await assert_intent(
            result,
            llm_client,
            intent="Asks for clarification about what type of registration (business, address, dog, etc.)",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_service_not_in_knowledge_base() -> None:
    """Test handling of service not in municipal domain."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Wie bekomme ich eine Pilotenlizenz?")
        await assert_intent(
            result,
            llm_client,
            intent="Responds to the pilot license question, either by declining (not a municipal service) or providing general information while noting it's outside municipal scope",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_specific_personal_case() -> None:
    """Test handling of complex personal situation."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Meine persönliche Situation ist sehr kompliziert. Was soll ich tun?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Suggests contacting the relevant office directly for complex personal situations requiring individual consultation",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_different_city() -> None:
    """Test handling of query about a different city."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(user_input="Was sind die Öffnungszeiten in Hamburg?")
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that information is only available for Lüneburg, not other cities",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_historical_query() -> None:
    """Test handling of historical information request."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie wurde dieser Service 1990 gehandhabt?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that only current information is available, not historical procedures",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_legal_interpretation() -> None:
    """Test handling of legal interpretation request."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ist es legal, wenn ich mein Gewerbe nicht anmelde?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides factual information about registration requirements and suggests legal consultation for complex legal questions",
        )


@pytest.mark.asyncio
async def test_multiple_services_at_once() -> None:
    """Test handling of multiple service requests."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich muss 5 verschiedene Dinge tun. Können Sie mir bei allem helfen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Offers to help systematically or asks the user to focus on one task at a time",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_contradictory_request() -> None:
    """Test handling of contradictory or illogical request."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ist das Amt offen, wenn es geschlossen ist?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Handles the contradictory query gracefully and provides helpful clarification",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_very_long_complex_query() -> None:
    """Test handling of very long, complex multi-part query."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin letzten Monat von Frankfurt hierher gezogen und habe vergessen mich anzumelden "
            "und jetzt brauche ich einen neuen Reisepass aber ich weiß nicht ob ich zuerst die Adresse "
            "oder den Reisepass machen soll und außerdem habe ich einen Hund und muss vielleicht auch ein "
            "Gewerbe anmelden..."
        )
        await assert_intent(
            result,
            llm_client,
            intent="Parses the complex query and addresses the main questions systematically, prioritizing address registration first",
        )


# ==============================================================================
# CATEGORY 5: EXACT NUMERIC FACTS - GROUNDING TESTS (10 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_death_certificate_exact_fees() -> None:
    """Test exact death certificate fees without approximation."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was kostet die erste Sterbeurkunde und jede weitere?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides exact fee of 15,00 EUR for first death certificate and 7,50 EUR for each additional copy ordered simultaneously",
        )


@pytest.mark.asyncio
async def test_business_tax_threshold_exact() -> None:
    """Test exact business tax threshold without rounding."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ab welchem Gewerbeertrag muss ich Gewerbesteuer zahlen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States that business tax is required for annual earnings of more than EUR 24.500 (mehr als EUR 24.500)",
        )


@pytest.mark.asyncio
async def test_wohngeld_percentage_threshold() -> None:
    """Test exact Wohngeld income change threshold."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Um wie viel Prozent muss sich mein Einkommen erhöhen, damit Wohngeld gekürzt wird?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States that income must increase by more than 15 percent (mehr als 15 Prozent) and the change must last longer than 4 months",
        )


@pytest.mark.asyncio
async def test_address_registration_deadline_days() -> None:
    """Test exact deadline for address registration."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie viele Tage habe ich nach dem Umzug für die Anmeldung?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States that registration must occur within 2 weeks (2 Wochen) or 14 days after moving",
        )


@pytest.mark.asyncio
async def test_dog_deregistration_deadline_exact() -> None:
    """Test exact deadline for dog deregistration."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Innerhalb welcher Frist muss ich meinen Hund abmelden?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States that dog deregistration must occur within 1 week (innerhalb einer Woche) of ceasing ownership",
        )


@pytest.mark.asyncio
async def test_dog_registration_fee_exact() -> None:
    """Test exact dog registration fee for Niedersächsisches Hunderegister."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was kostet die Anmeldung beim Niedersächsischen Hunderegister?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides exact fee of 14,50 EUR for registration in the Niedersächsisches Hunderegister",
        )


@pytest.mark.asyncio
async def test_einwohnermeldeamt_thursday_hours_exact() -> None:
    """Test exact opening hours for Einwohnermeldeamt on Thursday."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wann genau hat das Einwohnermeldeamt am Donnerstag geöffnet?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States exact Thursday hours for Einwohnermeldeamt: 08:00-12:00 and 14:00-18:00",
        )


@pytest.mark.asyncio
async def test_luenepark_parking_spaces_exact() -> None:
    """Test exact number of parking spaces at Lünepark."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie viele Parkplätze gibt es am Lünepark?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States exact numbers: 625 parking spaces total, including 11 disabled parking spaces at Lünepark",
        )


@pytest.mark.asyncio
async def test_death_register_retention_period() -> None:
    """Test exact retention period for death registers."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie lange werden Sterbebücher aufbewahrt?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States that death registers (Sterbebücher) are retained for 30 years (30 Jahre)",
        )


@pytest.mark.asyncio
async def test_business_tax_rate_calculation() -> None:
    """Test exact business tax rate calculation formula."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie wird die Gewerbesteuer berechnet?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains that business tax is calculated using 3.5 percent (3,5 Prozent) multiplied by the municipal Hebesatz",
        )


# ==============================================================================
# CATEGORY 6: HALLUCINATION PREVENTION - GUARDRAIL TESTS (8 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_nonexistent_fee_query() -> None:
    """Test that agent doesn't fabricate fees for non-existent services."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Was kostet die Anmeldung eines Fahrrads in Lüneburg?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that bicycle registration is not required or information is not available, without fabricating a fee",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_unavailable_processing_time_query() -> None:
    """Test that agent doesn't guess processing times when not in KB."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie lange dauert die Bearbeitung eines Reisepasses genau?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides processing time only if available in knowledge base, otherwise indicates it varies by workload (Unterschiedlich - je nach Arbeitslage) or suggests contacting the office",
        )


@pytest.mark.asyncio
async def test_nonexistent_department_hours() -> None:
    """Test that agent doesn't fabricate hours for departments not in KB."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wann hat das Gesundheitsamt geöffnet?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that opening hours for Gesundheitsamt are not available without fabricating times or using hours from other departments",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_phone_number_fabrication_prevention() -> None:
    """Test that agent doesn't invent contact information."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie lautet die Telefonnummer des Umweltamtes?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides phone number only if available in knowledge base, otherwise indicates it's not available without fabricating numbers",
        )


@pytest.mark.asyncio
async def test_missing_document_requirements() -> None:
    """Test handling of state-level services not in municipal KB."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Welche Dokumente brauche ich für einen Führerschein?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Indicates that driver's license (Führerschein) is a state matter, not municipal, without fabricating specific requirements",
            uses_tool=False,
        )


@pytest.mark.asyncio
async def test_incomplete_procedure_handling() -> None:
    """Test that agent only describes procedures with complete information."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Wie läuft genau die Baugenehmigung ab?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides building permit information only if complete details are available, otherwise indicates limited information or suggests contacting the office",
        )


@pytest.mark.asyncio
async def test_cross_reference_accuracy() -> None:
    """Test that agent doesn't confuse similar departments."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Kann ich beim Einwohnermeldeamt heiraten?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Clarifies that marriage (Heirat) is handled by Standesamt (Registry Office), not Einwohnermeldeamt",
        )


@pytest.mark.asyncio
async def test_date_specific_holiday_hours() -> None:
    """Test handling of holiday hours without specific data."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Hat das Bürgerbüro an Weihnachten geöffnet?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Addresses holiday hours question without fabricating specific Christmas hours, may indicate that offices are typically closed on public holidays",
        )


# ==============================================================================
# CATEGORY 7: COMPLEX RAG & CONDITIONAL LOGIC - HARD CASES (12 tests)
# ==============================================================================


@pytest.mark.asyncio
async def test_wohngeld_complex_conditions() -> None:
    """Test complex Wohngeld rules with percentage threshold and time window."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Mein Einkommen ist um 20% gesunken. Kann ich mehr Wohngeld beantragen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Confirms eligibility because 20% exceeds the 15% threshold, and mentions that change must last longer than 4 months",
        )


@pytest.mark.asyncio
async def test_business_tax_threshold_calculation() -> None:
    """Test business tax threshold with comparison logic."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Mein Gewerbeertrag ist 20.000 EUR. Muss ich Gewerbesteuer zahlen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="States no business tax required because 20.000 EUR is below the threshold of mehr als 24.500 EUR",
        )


@pytest.mark.asyncio
async def test_noise_restriction_weekend_conditions() -> None:
    """Test noise restrictions with day-of-week and equipment-type rules."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Darf ich am Sonntag um 15 Uhr meinen Rasen mähen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Addresses Sunday/holiday noise restrictions for lawn mowers, mentioning time rules that may apply",
        )


@pytest.mark.asyncio
async def test_death_certificate_eligibility_siblings() -> None:
    """Test death certificate eligibility for siblings with conditional clause."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin die Schwester der Verstorbenen. Kann ich eine Sterbeurkunde beantragen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Confirms that siblings can request death certificates if they can demonstrate a legitimate interest (berechtigtes Interesse glaubhaft machen)",
        )


@pytest.mark.asyncio
async def test_new_resident_service_sequence() -> None:
    """Test service sequencing for new residents."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin neu in Lüneburg und starte ein Gewerbe. Was muss ich zuerst tun?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Recommends registering address first (Anmeldung) within 2 weeks, then registering business (Gewerbe anmelden)",
        )


@pytest.mark.asyncio
async def test_death_certificate_fee_calculation() -> None:
    """Test tiered fee calculation for multiple certificates."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich brauche drei Sterbeurkunden. Was kostet das insgesamt?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Calculates total cost of 30,00 EUR (15,00 for first + 7,50 + 7,50 for second and third) or provides breakdown showing first certificate costs 15,00 EUR and additional two cost 7,50 EUR each",
        )


@pytest.mark.asyncio
async def test_dog_registration_age_threshold() -> None:
    """Test dog registration with age threshold and multiple requirements."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Mein Hund ist 7 Monate alt. Muss ich ihn schon anmelden?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Confirms that dogs must be registered at 6 months of age, so a 7-month-old dog requires registration",
        )


@pytest.mark.asyncio
async def test_opening_hours_multi_department_conflict() -> None:
    """Test finding compatible days across multiple departments."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="An welchem Tag kann ich sowohl das Standesamt als auch das Einwohnermeldeamt besuchen?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Identifies days when both Standesamt and Einwohnermeldeamt are open, analyzing their respective schedules",
        )


@pytest.mark.asyncio
async def test_residence_permit_freelancer_distinction() -> None:
    """Test distinguishing freelance from employee residence permits."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich bin Freiberufler aus Indien. Welche Aufenthaltserlaubnis brauche ich?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Addresses residence permit for freelancers (Freiberufler), distinguishing from employee permits if such information exists in knowledge base",
        )


@pytest.mark.asyncio
async def test_business_registration_timing_requirement() -> None:
    """Test business registration timing with at-time-of-start requirement."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Kann ich mein Gewerbe einen Monat vor Geschäftseröffnung anmelden?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Explains that business registration must occur at the time of business start (bei Aufnahme der Tätigkeit), addressing advance registration question",
        )


@pytest.mark.asyncio
async def test_noise_restriction_exception_clause() -> None:
    """Test noise restriction with EU eco-label equipment exception."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich habe ein Gartengerät mit EU-Umweltzeichen. Gelten die Lärmschutzzeiten trotzdem?"
        )
        await assert_intent(
            result,
            llm_client,
            intent="Addresses whether EU eco-labeled equipment (EU-Umweltzeichen) has exceptions to noise restrictions, providing relevant information if available",
        )


@pytest.mark.asyncio
async def test_cross_document_contact_synthesis() -> None:
    """Test synthesizing contact information across multiple offices."""
    async with session_and_llm() as (llm_client, session):
        result = await session.run(
            user_input="Ich brauche Kontaktdaten für Einwohnermeldeamt, Standesamt und Gewerbeamt."
        )
        await assert_intent(
            result,
            llm_client,
            intent="Provides contact information for all three offices (Einwohnermeldeamt, Standesamt, Gewerbeamt), synthesizing data from multiple sources",
        )
