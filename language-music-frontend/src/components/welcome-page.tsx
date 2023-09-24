import { useMemo } from "react";
import { Button } from "@mui/material";
import { useRouter } from "next/navigation";

const WelcomePage = () => {
  const router = useRouter();

  const availableLanguages: {[k: string]: string} = useMemo(
    () => ({
      de: "Deutsch",
      en: "English",
      fr: "Français",
      es: "Español",
      sw: "Svenska",
    }),
    [],
  );

  return (
    <div
      style={{
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        width: "200px",
      }}
    >
      {Object.keys(availableLanguages).map((k) => (
        <Button
          key={k}
          variant="outlined"
          onClick={() => {
            router.push(`?language=${k}`);
          }}
        >
          {availableLanguages[k]}
        </Button>
      ))}
    </div>
  );
};

export default WelcomePage;
