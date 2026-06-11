"""
Safe template reply generator for Phase 1.
All replies use pre-approved language — no invented pricing, features, or guarantees.
"""

from app.services.classifier import ClassificationResult


class ReplyGenerator:
    """Generate safe, template-based replies based on lead classification."""

    def generate(
        self,
        result: ClassificationResult,
        contact_name: str | None = None,
        contact_email: str | None = None,
        contact_phone: str | None = None,
    ) -> str:
        greeting = f"Hi {contact_name}," if contact_name else "Hello,"

        if result.lead_temperature == "hot":
            return self._hot_reply(greeting, result, contact_email, contact_phone)
        elif result.lead_temperature == "warm":
            return self._warm_reply(greeting, result)
        elif result.lead_temperature == "cold":
            return self._cold_reply(greeting)
        else:
            return self._not_lead_reply(greeting, result.intent)

    def _hot_reply(
        self,
        greeting: str,
        result: ClassificationResult,
        email: str | None,
        phone: str | None,
    ) -> str:
        intent = result.intent
        missing_info = []
        if not email:
            missing_info.append("your email address")
        if not phone:
            missing_info.append("your phone number")

        if intent == "demo_request":
            body = (
                "Thank you for your interest in a demo! Our sales team will be in touch with you "
                "shortly to arrange a convenient time."
            )
        elif intent in ("pricing_inquiry", "quotation_request"):
            body = (
                "Thank you for your enquiry about pricing. Our sales team will review your "
                "requirements and provide you with a tailored quotation."
            )
        elif intent == "sales_contact":
            body = (
                "Thank you for reaching out. A member of our sales team will contact you "
                "as soon as possible."
            )
        elif intent == "purchase_intent":
            body = (
                "Thank you for your interest in getting started! Our team will reach out to "
                "guide you through the next steps."
            )
        elif intent == "human_request":
            body = (
                "I am connecting you with our support team now. A team member will be with "
                "you shortly."
            )
        else:
            body = (
                "Thank you for your message. Our sales team will review your enquiry and "
                "get back to you shortly."
            )

        if missing_info:
            follow_up = f" To help us serve you better, could you please share {' and '.join(missing_info)}?"
        else:
            follow_up = " We look forward to speaking with you soon."

        return f"{greeting}\n\n{body}{follow_up}"

    def _warm_reply(self, greeting: str, result: ClassificationResult) -> str:
        intent = result.intent

        if intent == "feature_inquiry":
            body = (
                "Thank you for your interest! Our platform offers a range of features designed "
                "to help businesses in the tiles and flooring industry showcase their products "
                "effectively. I'd be happy to share more details."
            )
            question = "Which specific functionality are you most interested in learning about?"
        elif intent == "integration_inquiry":
            body = (
                "Great question about integrations! Our platform supports a variety of "
                "integrations to work seamlessly with your existing setup."
            )
            question = "Which platform or system are you looking to integrate with?"
        elif intent in ("ecommerce_integration",):
            body = (
                "We do have experience working with e-commerce platforms. Our team can discuss "
                "the best integration approach for your store."
            )
            question = "Are you looking to display a product catalogue, enable 3D visualization, or something else?"
        elif intent == "catalog_request":
            body = (
                "We can help you create a comprehensive digital product catalogue for your "
                "tiles and flooring range."
            )
            question = "Approximately how many products or SKUs would you like to include?"
        elif intent in ("technical_inquiry", "requirements_inquiry"):
            body = "I'd be happy to walk you through the technical details of our platform."
            question = "Could you share a bit more about your specific requirements or use case?"
        elif intent == "scale_inquiry":
            body = (
                "Understanding the scale of your operation helps us recommend the right solution."
            )
            question = "Could you tell me more about the size of your business or team?"
        else:
            body = (
                "Thank you for your enquiry! We work with businesses in the tiles and "
                "flooring industry to help them showcase products and engage customers effectively."
            )
            question = "What aspect of our platform are you most interested in exploring?"

        return f"{greeting}\n\n{body}\n\n{question}"

    def _cold_reply(self, greeting: str) -> str:
        return (
            f"{greeting}\n\n"
            "Thank you for reaching out! We are always happy to share more about what we do. "
            "What would you like to know about our platform?"
        )

    def _not_lead_reply(self, greeting: str, intent: str) -> str:
        if intent == "job_inquiry":
            return (
                f"{greeting}\n\n"
                "Thank you for your interest in joining our team. For career opportunities, "
                "please visit our website's careers section or reach out to our HR team directly."
            )
        if intent == "automated_message":
            return ""
        return (
            f"{greeting}\n\n"
            "Thank you for your message. We have received it and will respond "
            "if any follow-up is needed."
        )
