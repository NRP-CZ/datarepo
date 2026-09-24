import React from "react";
import { forwardRef } from "react";
import { Ref } from "semantic-ui-react";

export function withSemanticUIForwardDOMRef(Component) {
  return forwardRef(function WithSemanticUIForwardDOMRef(props, ref) {
    return (
      <Ref innerRef={ref}>
        <Component {...props} />
      </Ref>
    );
  });
}

export default withSemanticUIForwardDOMRef;
