"""Unit tests for the deterministic lead classifier."""

import pytest

from app.services.classifier import LeadClassifier


@pytest.fixture
def classifier():
    return LeadClassifier()


def test_hot_lead_demo_request(classifier):
    result = classifier.classify("I would like to book a demo please")
    assert result.lead_temperature == "hot"
    assert result.is_lead is True
    assert result.handoff_required is True
    assert result.lead_score >= 70


def test_hot_lead_pricing_request(classifier):
    result = classifier.classify("What is the pricing for your platform?")
    assert result.lead_temperature == "hot"
    assert result.handoff_required is True


def test_hot_lead_purchase_intent(classifier):
    result = classifier.classify("I want to buy your product and sign up today")
    assert result.lead_temperature == "hot"
    assert result.handoff_required is True


def test_hot_lead_human_request(classifier):
    result = classifier.classify("Can I speak to a human agent please?")
    assert result.lead_temperature == "hot"
    assert result.handoff_required is True


def test_hot_lead_sales_call(classifier):
    result = classifier.classify("Please call me, I want to discuss a sales call")
    assert result.lead_temperature == "hot"
    assert result.handoff_required is True


def test_warm_lead_feature_inquiry(classifier):
    result = classifier.classify("What features does your platform have for tile designers?")
    assert result.lead_temperature == "warm"
    assert result.is_lead is True
    assert result.handoff_required is False


def test_warm_lead_integration(classifier):
    result = classifier.classify("Does your product integrate with Shopify?")
    assert result.lead_temperature == "warm"
    assert result.is_lead is True


def test_warm_lead_technical(classifier):
    result = classifier.classify("How does the 3D viewer work technically?")
    assert result.lead_temperature in ("warm", "hot")
    assert result.is_lead is True


def test_cold_lead_general_interest(classifier):
    result = classifier.classify("I'm interested in your product")
    assert result.lead_temperature == "cold"
    assert result.is_lead is True
    assert result.handoff_required is False


def test_cold_lead_positive_comment(classifier):
    result = classifier.classify("Looks great! Nice product.")
    assert result.lead_temperature == "cold"
    assert result.handoff_required is False


def test_not_lead_job_enquiry(classifier):
    result = classifier.classify("I am looking for a job, here is my resume")
    assert result.lead_temperature == "not_lead"
    assert result.is_lead is False


def test_not_lead_spam_marketing(classifier):
    result = classifier.classify("We offer SEO services and link building to rank your website")
    assert result.lead_temperature == "not_lead"
    assert result.is_lead is False


def test_not_lead_automated_message(classifier):
    result = classifier.classify("This is an automated message, do not reply")
    assert result.lead_temperature == "not_lead"
    assert result.is_lead is False


def test_quotation_request_handoff(classifier):
    result = classifier.classify("Can you send me a quotation for 10 stores?")
    assert result.handoff_required is True
    assert result.lead_temperature == "hot"
