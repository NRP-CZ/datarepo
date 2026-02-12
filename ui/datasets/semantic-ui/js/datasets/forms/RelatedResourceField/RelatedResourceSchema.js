import {
  Field,
  SchemaField,
  VocabularyField,
  AllowAdditionsVocabularyField,
  FundingField,
  RightsVocabularyField,
} from "@js/invenio_rdm_records/src/deposit/serializers";

export const RelatedResourceSchema = {
  relation_type: new VocabularyField({
    fieldpath: "relation_type",
    deserializedDefault: "",
    serializedDefault: "",
  }),
  title: new Field({
    fieldpath: "title",
    deserializedDefault: "",
  }),
  additional_titles: new SchemaField({
    fieldpath: "additional_titles",
    schema: {
      title: new Field({
        fieldpath: "title",
      }),
      type: new VocabularyField({
        fieldpath: "type",
        deserializedDefault: "",
        serializedDefault: "",
      }),
      lang: new VocabularyField({
        fieldpath: "lang",
        deserializedDefault: "",
        serializedDefault: "",
      }),
    },
  }),
  additional_descriptions: new SchemaField({
    fieldpath: "additional_descriptions",
    schema: {
      description: new Field({
        fieldpath: "description",
      }),
      type: new VocabularyField({
        fieldpath: "type",
        deserializedDefault: "",
        serializedDefault: "",
      }),
      lang: new VocabularyField({
        fieldpath: "lang",
        deserializedDefault: "",
        serializedDefault: "",
      }),
    },
  }),
  creators: new SchemaField({
    fieldpath: "creators",
    schema: {
      person_or_org: new Field({
        fieldpath: "person_or_org",
      }),
      role: new VocabularyField({
        fieldpath: "role",
        deserializedDefault: "",
        serializedDefault: "",
      }),
      affiliations: new AllowAdditionsVocabularyField({
        fieldpath: "affiliations",
        deserializedDefault: [],
        serializedDefault: [],
        labelField: "name",
      }),
    },
  }),
  contributors: new SchemaField({
    fieldpath: "contributors",
    schema: {
      person_or_org: new Field({
        fieldpath: "person_or_org",
      }),
      role: new VocabularyField({
        fieldpath: "role",
        deserializedDefault: "",
        serializedDefault: "",
      }),
      affiliations: new AllowAdditionsVocabularyField({
        fieldpath: "affiliations",
        deserializedDefault: [],
        serializedDefault: [],
        labelField: "name",
      }),
    },
  }),
  resource_type: new VocabularyField({
    fieldpath: "resource_type",
    deserializedDefault: "",
    serializedDefault: "",
  }),
  publication_date: new Field({
    fieldpath: "publication_date",
    deserializedDefault: "",
  }),
  publisher: new Field({
    fieldpath: "publisher",
    deserializedDefault: "",
  }),
  dates: new SchemaField({
    fieldpath: "dates",
    schema: {
      date: new Field({
        fieldpath: "date",
      }),
      type: new VocabularyField({
        fieldpath: "type",
        deserializedDefault: "",
        serializedDefault: "",
      }),
      description: new Field({
        fieldpath: "description",
      }),
    },
    deserializedDefault: [],
  }),
  languages: new VocabularyField({
    fieldpath: "languages",
    deserializedDefault: [],
    serializedDefault: [],
  }),
  identifiers: new SchemaField({
    fieldpath: "identifiers",
    schema: {
      scheme: new Field({
        fieldpath: "scheme",
      }),
      identifier: new Field({
        fieldpath: "identifier",
      }),
    },
    deserializedDefault: [],
  }),
  subjects: new AllowAdditionsVocabularyField({
    fieldpath: "subjects",
    deserializedDefault: [],
    serializedDefault: [],
    labelField: "subject",
  }),
  funding: new SchemaField({
    fieldpath: "funding",
    schema: {
      award: new FundingField({
        fieldpath: "award",
        deserializedDefault: {},
      }),
      funder: new FundingField({
        fieldpath: "funder",
        deserializedDefault: {},
      }),
    },
  }),
  rights: new RightsVocabularyField({
    fieldpath: "rights",
    deserializedDefault: [],
    serializedDefault: [],
    localeFields: ["title", "description"],
  }),
};
