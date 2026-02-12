import { i18next } from "@translations/i18next";
import React from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Label, List, Ref } from "semantic-ui-react";
import { RelatedResourceModal } from "./RelatedResourceModal";
import PropTypes from "prop-types";
import { NestedErrors } from "@js/oarepo_ui/forms";

export const RelatedResourceFieldItem = ({
  compKey,
  index,
  replaceResource,
  removeResource,
  moveResource,
  addLabel,
  editLabel,
  initialResource,
  displayName,
  vocabularies,
  handleSave,
  relatedResourceUI,
}) => {
  const dropRef = React.useRef(null);
  const [_, drag, preview] = useDrag({
    item: { index, type: "relatedResource" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "relatedResource",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveResource(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  const getRelationTypeLabel = (relationType) => {
    if (!relationType) return "";
    const relationOptions = vocabularies?.relationtypes || [];
    const found = relationOptions.find(
      (opt) => opt.value === relationType.id || opt.value === relationType,
    );
    return found?.text || relationType.id || relationType;
  };

  const relationTypeLabel = getRelationTypeLabel(
    initialResource?.relation_type,
  );

  drop(dropRef);
  return (
    <Ref innerRef={dropRef} key={compKey}>
      <React.Fragment>
        <List.Item
          key={compKey}
          className={
            hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"
          }
        >
          <List.Content floated="right">
            <RelatedResourceModal
              handleSave={handleSave}
              compKey={compKey}
              index={index}
              relatedResourceUI={relatedResourceUI}
              addLabel={addLabel}
              editLabel={editLabel}
              onResourceChange={(selectedResource) => {
                replaceResource(index, selectedResource);
              }}
              initialResource={initialResource}
              vocabularies={vocabularies}
              action="edit"
              trigger={
                <Button size="mini" primary type="button">
                  {i18next.t("Edit")}
                </Button>
              }
            />
            <Button
              size="mini"
              type="button"
              onClick={() => removeResource(index)}
            >
              {i18next.t("Remove")}
            </Button>
          </List.Content>
          <Ref innerRef={drag}>
            <List.Icon name="bars" className="drag-anchor" />
          </Ref>
          <Ref innerRef={preview}>
            <List.Content>
              <List.Description>
                <span className="related-resource">
                  <span>{displayName}</span>
                  {relationTypeLabel && (
                    <Label size="tiny" className="ml-5">
                      {relationTypeLabel}
                    </Label>
                  )}
                </span>
              </List.Description>
            </List.Content>
          </Ref>
        </List.Item>
        <NestedErrors fieldPath={compKey} />
      </React.Fragment>
    </Ref>
  );
};

RelatedResourceFieldItem.propTypes = {
  compKey: PropTypes.string.isRequired,
  index: PropTypes.number.isRequired,
  replaceResource: PropTypes.func.isRequired,
  removeResource: PropTypes.func.isRequired,
  moveResource: PropTypes.func.isRequired,
  initialResource: PropTypes.object.isRequired,
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  displayName: PropTypes.string,
  vocabularies: PropTypes.object,
  handleSave: PropTypes.func.isRequired,
  relatedResourceUI: PropTypes.object,
};
