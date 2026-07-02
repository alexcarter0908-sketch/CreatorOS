"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import CreateProjectDialog from "./CreateProjectDialog";

export default function CreateProjectButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        + New Project
      </Button>

      <CreateProjectDialog
        open={open}
        onOpenChange={setOpen}
      />
    </>
  );
}