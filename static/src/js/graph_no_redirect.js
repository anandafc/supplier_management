/** @odoo-module **/

import { GraphView } from "@web/views/graph/graph_view";

class DisableRedirectGraph extends GraphView {
    setup() {
        super.setup();
        this.onGraphClick = () => {};  // Override the click handler with an empty function
    }
}

DisableRedirectGraph.template = GraphView.template;
DisableRedirectGraph.props = GraphView.props;
DisableRedirectGraph.type = GraphView.type;
DisableRedirectGraph.display_name = GraphView.display_name;
DisableRedirectGraph.icon = GraphView.icon;

export default DisableRedirectGraph;
